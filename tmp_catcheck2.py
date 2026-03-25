import base64

php = b"""<?php
require __DIR__ . '/app/bootstrap.php';
$b = \\Magento\\Framework\\App\\Bootstrap::create(BP, $_SERVER);
$o = $b->getObjectManager();
$c = $o->create(\\Magento\\Catalog\\Model\\ResourceModel\\Category\\CollectionFactory::class)->create();
$c->addAttributeToSelect(['name','url_key','display_mode','is_anchor','is_active','children_count']);
$c->addAttributeToFilter('parent_id', 4);
foreach ($c as $cat) {
    echo "SUB: id=" . $cat->getId() . " key=" . $cat->getUrlKey() . " name=" . $cat->getName() . " mode=" . $cat->getDisplayMode() . " anchor=" . $cat->getIsAnchor() . " active=" . $cat->getIsActive() . "\\n";
}
"""

print(base64.b64encode(php).decode())
