<?php
declare(strict_types=1);

/**
 * Sync one CMS page content from live GraphQL into test DB.
 *
 * Usage:
 *   php sync_cms_page_from_live.php \
 *     --env=/home/vibeadd/vibeadd.com/hyvatestproject/app/etc/env.php \
 *     --identifier=home-de \
 *     --graphql=https://shop.ftc-cashmere.com/graphql
 */

if (PHP_SAPI !== 'cli') {
    fwrite(STDERR, "CLI only\n");
    exit(1);
}

function requiredOpt(array $opts, string $name): string
{
    if (!isset($opts[$name]) || trim((string) $opts[$name]) === '') {
        fwrite(STDERR, "Missing required option --{$name}\n");
        exit(1);
    }
    return (string) $opts[$name];
}

function graphql(string $endpoint, string $identifier): array
{
    $query = <<<'GQL'
query($identifier: String!) {
  cmsPage(identifier: $identifier) {
    identifier
    title
    content
  }
}
GQL;

    $payload = json_encode([
        'query' => $query,
        'variables' => ['identifier' => $identifier],
    ], JSON_UNESCAPED_SLASHES);

    if ($payload === false) {
        throw new RuntimeException('Failed to encode GraphQL payload');
    }

    $ch = curl_init($endpoint);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_POSTFIELDS => $payload,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_CONNECTTIMEOUT => 15,
        CURLOPT_TIMEOUT => 120,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_SSL_VERIFYHOST => 2,
        CURLOPT_USERAGENT => 'hyva-cms-page-sync/1.0',
    ]);

    $raw = curl_exec($ch);
    $err = curl_error($ch);
    $status = (int) curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    curl_close($ch);

    if (!is_string($raw)) {
        throw new RuntimeException("GraphQL request failed: {$err}");
    }
    if ($status < 200 || $status >= 300) {
        throw new RuntimeException("GraphQL HTTP {$status}");
    }

    $json = json_decode($raw, true);
    if (!is_array($json)) {
        throw new RuntimeException('GraphQL JSON decode failed');
    }
    if (!empty($json['errors'])) {
        throw new RuntimeException('GraphQL errors: ' . json_encode($json['errors']));
    }

    $page = $json['data']['cmsPage'] ?? null;
    if (!is_array($page) || empty($page['identifier'])) {
        throw new RuntimeException("CMS page '{$identifier}' not found in live GraphQL");
    }

    return $page;
}

$opts = getopt('', ['env:', 'identifier:', 'graphql::']);
$envFile = requiredOpt($opts, 'env');
$identifier = requiredOpt($opts, 'identifier');
$graphqlEndpoint = (string) ($opts['graphql'] ?? 'https://shop.ftc-cashmere.com/graphql');

if (!is_file($envFile)) {
    throw new RuntimeException("env.php not found: {$envFile}");
}

$env = include $envFile;
$db = $env['db']['connection']['default'] ?? null;
if (!is_array($db)) {
    throw new RuntimeException('DB config missing in env.php');
}

$livePage = graphql($graphqlEndpoint, $identifier);
$liveTitle = (string) ($livePage['title'] ?? '');
$liveContent = (string) ($livePage['content'] ?? '');

$pdo = new PDO(
    sprintf('mysql:host=%s;dbname=%s;charset=utf8mb4', (string) $db['host'], (string) $db['dbname']),
    (string) $db['username'],
    (string) ($db['password'] ?? ''),
    [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]
);

$select = $pdo->prepare('SELECT page_id, title, LENGTH(content) AS len FROM cms_page WHERE identifier = :identifier');
$select->execute(['identifier' => $identifier]);
$current = $select->fetch();
if (!$current) {
    throw new RuntimeException("CMS page '{$identifier}' not found on test DB");
}

$update = $pdo->prepare(
    'UPDATE cms_page
        SET title = :title,
            content = :content,
            update_time = NOW()
      WHERE page_id = :page_id'
);
$update->execute([
    'title' => $liveTitle,
    'content' => $liveContent,
    'page_id' => (int) $current['page_id'],
]);

$result = [
    'identifier' => $identifier,
    'page_id' => (int) $current['page_id'],
    'old_length' => (int) $current['len'],
    'new_length' => strlen($liveContent),
    'title' => $liveTitle,
];

echo json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . PHP_EOL;
