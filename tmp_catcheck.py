import base64

php = b"""<?php
require __DIR__ . '/app/bootstrap.php';
$b = \\Magento\\Framework\\App\\Bootstrap::create(BP, $_SERVER);
$o = $b->getObjectManager();
$c = $o->create(\\Magento\\Catalog\\Model\\ResourceModel\\Category\\CollectionFactory::class)->create();
$c->addAttributeToSelect(['name','url_key','display_mode','is_anchor','is_active']);
$c->addAttributeToFilter('url_key', ['like' => '%ready%']);
foreach ($c as $cat) {
    echo "CAT: id=" . $cat->getId() . " name=" . $cat->getName() . " mode=" . $cat->getDisplayMode() . " anchor=" . $cat->getIsAnchor() . " active=" . $cat->getIsActive() . "\\n";
}
$d = $o->create(\\Magento\\Catalog\\Model\\ResourceModel\\Category\\CollectionFactory::class)->create();
$d->addAttributeToSelect(['name','url_key','display_mode','is_anchor']);
$d->addAttributeToFilter('url_key', 'damen');
foreach ($d as $cat) {
    echo "DAMEN: id=" . $cat->getId() . " name=" . $cat->getName() . " mode=" . $cat->getDisplayMode() . " anchor=" . $cat->getIsAnchor() . "\\n";
}
"""

print(base64.b64encode(php).decode())
