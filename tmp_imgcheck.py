import base64

php = b"""<?php
require __DIR__ . '/app/bootstrap.php';
$b = \\Magento\\Framework\\App\\Bootstrap::create(BP, $_SERVER);
$o = $b->getObjectManager();
$resource = $o->get(\\Magento\\Framework\\App\\ResourceConnection::class);
$conn = $resource->getConnection();

// Check how many gallery entries product SKU 00002-1000 has
$select = $conn->select()
    ->from(['mg' => $resource->getTableName('catalog_product_entity_media_gallery')], ['mg.value_id', 'mg.value', 'mg.media_type'])
    ->join(['mgv' => $resource->getTableName('catalog_product_entity_media_gallery_value')], 'mg.value_id = mgv.value_id', ['mgv.disabled', 'mgv.position', 'mgv.store_id'])
    ->join(['mgvte' => $resource->getTableName('catalog_product_entity_media_gallery_value_to_entity')], 'mg.value_id = mgvte.value_id', ['mgvte.entity_id'])
    ->join(['pe' => $resource->getTableName('catalog_product_entity')], 'pe.entity_id = mgvte.entity_id', ['pe.sku'])
    ->where('pe.sku = ?', '00002-1000')
    ->order('mgv.position ASC');

$rows = $conn->fetchAll($select);
foreach ($rows as $row) {
    echo "IMG: sku=" . $row['sku'] . " file=" . $row['value'] . " pos=" . $row['position'] . " disabled=" . $row['disabled'] . " store=" . $row['store_id'] . "\\n";
}

// Count total per first 5 products
$select2 = $conn->select()
    ->from(['mg' => $resource->getTableName('catalog_product_entity_media_gallery')], ['cnt' => 'COUNT(DISTINCT mg.value_id)'])
    ->join(['mgvte' => $resource->getTableName('catalog_product_entity_media_gallery_value_to_entity')], 'mg.value_id = mgvte.value_id', ['mgvte.entity_id'])
    ->join(['pe' => $resource->getTableName('catalog_product_entity')], 'pe.entity_id = mgvte.entity_id', ['pe.sku'])
    ->where('pe.sku IN (?)', ['00002-1000', '00002-3100', '00006-1160', '00006-1300', '00006-2150'])
    ->group('pe.sku');

$rows2 = $conn->fetchAll($select2);
foreach ($rows2 as $row) {
    echo "COUNT: sku=" . $row['sku'] . " images=" . $row['cnt'] . "\\n";
}
"""

print(base64.b64encode(php).decode())
