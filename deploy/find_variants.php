<?php
$pdo = new PDO(
    'mysql:host=vibeadd.mysql.tools;dbname=vibeadd_02022026vibeaddcom',
    'vibeadd_02022026vibeaddcom',
    'e_99UmXv9#'
);
$sql = "
SELECT 
    parent.entity_id as pid,
    v_name.value as name,
    url.value as url_key,
    COUNT(DISTINCT eav_int.value) as colors
FROM catalog_product_entity parent
JOIN catalog_product_super_link sl ON parent.entity_id = sl.parent_id
JOIN catalog_product_entity child ON sl.product_id = child.entity_id
JOIN catalog_product_entity_int eav_int ON child.entity_id = eav_int.entity_id 
    AND eav_int.attribute_id = 173 AND eav_int.store_id = 0
JOIN catalog_product_entity_varchar v_name ON parent.entity_id = v_name.entity_id 
    AND v_name.attribute_id = 73 AND v_name.store_id = 0
LEFT JOIN catalog_product_entity_varchar url ON parent.entity_id = url.entity_id 
    AND url.attribute_id = 97 AND url.store_id = 0
WHERE parent.type_id = 'configurable'
GROUP BY parent.entity_id, v_name.value, url.value
HAVING colors > 1
ORDER BY colors DESC
LIMIT 15
";
$rows = $pdo->query($sql)->fetchAll(PDO::FETCH_ASSOC);
foreach ($rows as $r) {
    echo $r['pid'] . ' | ' . $r['colors'] . ' colors | ' . $r['name'] . ' | ' . $r['url_key'] . "\n";
}
