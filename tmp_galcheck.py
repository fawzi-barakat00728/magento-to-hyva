import base64

php = b"""<?php
require __DIR__ . '/app/bootstrap.php';
$b = \\Magento\\Framework\\App\\Bootstrap::create(BP, $_SERVER);
$o = $b->getObjectManager();

// Load category 162 (Ready to wear)
$cat = $o->create(\\Magento\\Catalog\\Model\\CategoryFactory::class)->create()->load(162);
$prodCollection = $cat->getProductCollection();
$prodCollection->addAttributeToSelect('*');
$prodCollection->setPageSize(5);
$prodCollection->addMediaGalleryData();

foreach ($prodCollection as $p) {
    $gallery = $p->getMediaGalleryImages();
    $count = $gallery ? count($gallery) : 0;
    $urls = [];
    if ($gallery) {
        foreach ($gallery as $img) {
            $urls[] = basename($img->getFile());
        }
    }
    echo "PROD: " . $p->getSku() . " gallery_count=" . $count . " imgs=" . implode(",", $urls) . "\\n";
}
"""

print(base64.b64encode(php).decode())
