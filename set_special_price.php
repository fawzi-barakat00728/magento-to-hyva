<?php
require 'app/bootstrap.php';
$bootstrap = \Magento\Framework\App\Bootstrap::create(BP, $_SERVER);
$obj = $bootstrap->getObjectManager();

$state = $obj->get(\Magento\Framework\App\State::class);
try { $state->setAreaCode('adminhtml'); } catch (\Exception $e) {}

$repo = $obj->get(\Magento\Catalog\Api\ProductRepositoryInterface::class);
$storeManager = $obj->get(\Magento\Store\Model\StoreManagerInterface::class);
$storeManager->setCurrentStore(0);

// Check parent configurable product
$p = $repo->get('10004-0460');
echo "Parent SKU: " . $p->getSku() . "\n";
echo "Parent ID: " . $p->getId() . "\n";
echo "Parent status: " . $p->getStatus() . "\n";
echo "Parent visibility: " . $p->getVisibility() . "\n";
echo "Parent price: " . $p->getPrice() . "\n";
echo "Parent special_price: " . $p->getSpecialPrice() . "\n";

// Check URL rewrites
$urlRewrite = $obj->get(\Magento\UrlRewrite\Model\ResourceModel\UrlRewriteCollectionFactory::class);
$collection = $urlRewrite->create();
$collection->addFieldToFilter('entity_type', 'product');
$collection->addFieldToFilter('entity_id', $p->getId());
echo "\nURL rewrites:\n";
foreach ($collection as $rewrite) {
    echo "  store=" . $rewrite->getStoreId() . " path=" . $rewrite->getRequestPath() . " target=" . $rewrite->getTargetPath() . "\n";
}

// Check children
$children = $p->getTypeInstance()->getUsedProducts($p);
foreach ($children as $c) {
    echo "\nChild: " . $c->getSku() . " status=" . $c->getStatus() . " price=" . $c->getPrice() . " special=" . $c->getSpecialPrice() . "\n";
}

// Check store assignments
$websites = $p->getWebsiteIds();
echo "\nWebsite IDs: " . implode(',', $websites) . "\n";
echo "Done\n";
