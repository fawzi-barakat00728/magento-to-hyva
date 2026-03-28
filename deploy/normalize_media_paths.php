<?php
declare(strict_types=1);

/**
 * Normalize migrated product media paths from "/cache/<hash>/..." to "/...".
 * Also deduplicates gallery links by (entity_id, media value).
 *
 * Usage:
 *   php normalize_media_paths.php --env=/path/to/app/etc/env.php
 *   php normalize_media_paths.php --dsn='mysql:host=...;dbname=...;charset=utf8mb4' --user=... --pass=...
 */

if (PHP_SAPI !== 'cli') {
    fwrite(STDERR, "CLI only\n");
    exit(1);
}

$opts = getopt('', ['env::', 'dsn::', 'user::', 'pass::']);

function fail(string $message, int $code = 1): void
{
    fwrite(STDERR, $message . PHP_EOL);
    exit($code);
}

function connectFromEnv(string $envFile): PDO
{
    if (!is_file($envFile)) {
        fail("env.php not found: {$envFile}");
    }
    $env = include $envFile;
    $db = $env['db']['connection']['default'] ?? null;
    if (!is_array($db)) {
        fail('Invalid DB config in env.php');
    }

    return new PDO(
        sprintf(
            'mysql:host=%s;dbname=%s;charset=utf8mb4',
            (string) ($db['host'] ?? 'localhost'),
            (string) ($db['dbname'] ?? '')
        ),
        (string) ($db['username'] ?? ''),
        (string) ($db['password'] ?? ''),
        [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        ]
    );
}

function connectFromDsn(string $dsn, string $user, string $pass): PDO
{
    return new PDO(
        $dsn,
        $user,
        $pass,
        [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        ]
    );
}

if (!empty($opts['env'])) {
    $pdo = connectFromEnv((string) $opts['env']);
} elseif (!empty($opts['dsn']) && isset($opts['user']) && array_key_exists('pass', $opts)) {
    $pdo = connectFromDsn((string) $opts['dsn'], (string) $opts['user'], (string) $opts['pass']);
} else {
    fail('Provide --env=<path> OR --dsn/--user/--pass');
}

$countCacheMediaSql = "SELECT COUNT(*) FROM catalog_product_entity_media_gallery WHERE value REGEXP '^/cache/[^/]+/'";
$countCacheAttrsSql = "
SELECT COUNT(*)
FROM catalog_product_entity_varchar v
JOIN eav_attribute a ON a.attribute_id = v.attribute_id
JOIN eav_entity_type t ON t.entity_type_id = a.entity_type_id
WHERE t.entity_type_code = 'catalog_product'
  AND a.attribute_code IN ('image','small_image','thumbnail','swatch_image')
  AND v.value REGEXP '^/cache/[^/]+/'
";
$countDuplicateEntityMediaSql = "
SELECT COUNT(*) FROM (
  SELECT vte.entity_id, mg.value, COUNT(*) c
  FROM catalog_product_entity_media_gallery_value_to_entity vte
  JOIN catalog_product_entity_media_gallery mg ON mg.value_id = vte.value_id
  GROUP BY vte.entity_id, mg.value
  HAVING c > 1
) t
";

$beforeMedia = (int) $pdo->query($countCacheMediaSql)->fetchColumn();
$beforeAttrs = (int) $pdo->query($countCacheAttrsSql)->fetchColumn();
$beforeDuplicates = (int) $pdo->query($countDuplicateEntityMediaSql)->fetchColumn();

echo "Before\n";
echo "  cache-prefixed media_gallery rows: {$beforeMedia}\n";
echo "  cache-prefixed image attribute rows: {$beforeAttrs}\n";
echo "  duplicate entity+media groups: {$beforeDuplicates}\n";

$pdo->beginTransaction();

try {
    $updateAttrsSql = "
    UPDATE catalog_product_entity_varchar v
    JOIN eav_attribute a ON a.attribute_id = v.attribute_id
    JOIN eav_entity_type t ON t.entity_type_id = a.entity_type_id
    SET v.value = REGEXP_REPLACE(v.value, '^/cache/[^/]+/', '/')
    WHERE t.entity_type_code = 'catalog_product'
      AND a.attribute_code IN ('image','small_image','thumbnail','swatch_image')
      AND v.value REGEXP '^/cache/[^/]+/'
    ";
    $updatedAttrs = (int) $pdo->exec($updateAttrsSql);

    $updateMediaSql = "
    UPDATE catalog_product_entity_media_gallery
    SET value = REGEXP_REPLACE(value, '^/cache/[^/]+/', '/')
    WHERE value REGEXP '^/cache/[^/]+/'
    ";
    $updatedMedia = (int) $pdo->exec($updateMediaSql);

    $deleteDuplicateLinksSql = "
    DELETE vte_dup
    FROM catalog_product_entity_media_gallery_value_to_entity vte_dup
    JOIN catalog_product_entity_media_gallery mg_dup ON mg_dup.value_id = vte_dup.value_id
    JOIN catalog_product_entity_media_gallery_value_to_entity vte_keep ON vte_keep.entity_id = vte_dup.entity_id
    JOIN catalog_product_entity_media_gallery mg_keep
      ON mg_keep.value_id = vte_keep.value_id
     AND mg_keep.value = mg_dup.value
    WHERE mg_keep.value_id < mg_dup.value_id
    ";
    $deletedDuplicateLinks = (int) $pdo->exec($deleteDuplicateLinksSql);

    $deleteDuplicateValueRowsSql = "
    DELETE mgv_dup
    FROM catalog_product_entity_media_gallery_value mgv_dup
    JOIN catalog_product_entity_media_gallery mg_dup ON mg_dup.value_id = mgv_dup.value_id
    JOIN catalog_product_entity_media_gallery_value mgv_keep
      ON mgv_keep.entity_id = mgv_dup.entity_id
     AND mgv_keep.store_id = mgv_dup.store_id
    JOIN catalog_product_entity_media_gallery mg_keep
      ON mg_keep.value_id = mgv_keep.value_id
     AND mg_keep.value = mg_dup.value
    WHERE mg_keep.value_id < mg_dup.value_id
    ";
    $deletedDuplicateValueRows = (int) $pdo->exec($deleteDuplicateValueRowsSql);

    $deleteOrphanMediaSql = "
    DELETE mg
    FROM catalog_product_entity_media_gallery mg
    LEFT JOIN catalog_product_entity_media_gallery_value_to_entity vte ON vte.value_id = mg.value_id
    WHERE vte.value_id IS NULL
    ";
    $deletedOrphanMedia = (int) $pdo->exec($deleteOrphanMediaSql);

    $pdo->commit();
} catch (Throwable $e) {
    $pdo->rollBack();
    fail('Failed: ' . $e->getMessage());
}

$afterMedia = (int) $pdo->query($countCacheMediaSql)->fetchColumn();
$afterAttrs = (int) $pdo->query($countCacheAttrsSql)->fetchColumn();
$afterDuplicates = (int) $pdo->query($countDuplicateEntityMediaSql)->fetchColumn();

echo "\nUpdated\n";
echo "  normalized media_gallery rows: {$updatedMedia}\n";
echo "  normalized image attribute rows: {$updatedAttrs}\n";
echo "  deleted duplicate links: {$deletedDuplicateLinks}\n";
echo "  deleted duplicate value rows: {$deletedDuplicateValueRows}\n";
echo "  deleted orphan media rows: {$deletedOrphanMedia}\n";

echo "\nAfter\n";
echo "  cache-prefixed media_gallery rows: {$afterMedia}\n";
echo "  cache-prefixed image attribute rows: {$afterAttrs}\n";
echo "  duplicate entity+media groups: {$afterDuplicates}\n";

echo "\nDone.\n";
