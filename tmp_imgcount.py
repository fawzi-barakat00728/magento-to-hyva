import base64

php = b"""<?php
require __DIR__ . '/app/bootstrap.php';
$b = \\Magento\\Framework\\App\\Bootstrap::create(BP, $_SERVER);
$o = $b->getObjectManager();
$resource = $o->get(\\Magento\\Framework\\App\\ResourceConnection::class);
$conn = $resource->getConnection();

// Count gallery images for first 10 products that have the most images
$select = $conn->select()
    ->from(['mg' => $resource->getTableName('catalog_product_entity_media_gallery')], ['cnt' => 'COUNT(DISTINCT mg.value_id)'])
    ->join(['mgvte' => $resource->getTableName('catalog_product_entity_media_gallery_value_to_entity')], 'mg.value_id = mgvte.value_id', ['mgvte.entity_id'])
    ->join(['pe' => $resource->getTableName('catalog_product_entity')], 'pe.entity_id = mgvte.entity_id', ['pe.sku'])
    ->group('pe.sku')
    ->order('cnt DESC')
    ->limit(10);

$rows = $conn->fetchAll($select);
foreach ($rows as $row) {
    echo "TOP: sku=" . $row['sku'] . " images=" . $row['cnt'] . "\\n";
}

// Also count total products that have more than 1 image
$select2 = $conn->select()
    ->from(['mg' => $resource->getTableName('catalog_product_entity_media_gallery')], ['cnt' => 'COUNT(DISTINCT mg.value_id)'])
    ->join(['mgvte' => $resource->getTableName('catalog_product_entity_media_gallery_value_to_entity')], 'mg.value_id = mgvte.value_id', [])
    ->group('mgvte.entity_id')
    ->having('cnt > 1');
echo "Products with >1 image: " . count($conn->fetchAll($select2)) . "\\n";
"""

print(base64.b64encode(php).decode())
