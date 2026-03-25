<?php

declare(strict_types=1);

namespace MediaDivision\PaginationFix\Plugin;

use Amasty\Shopby\Model\ResourceModel\Fulltext\Collection;
use Magento\Framework\Search\EngineResolverInterface;

/**
 * Fix: Amasty Shopby checks for engine 'mysql' but Magento 2.4.8 uses 'mysql2'.
 * Without this, SQL LIMIT is never applied and all products load on category pages.
 */
class FixAmastyPagination
{
    private EngineResolverInterface $engineResolver;

    public function __construct(EngineResolverInterface $engineResolver)
    {
        $this->engineResolver = $engineResolver;
    }

    /**
     * @SuppressWarnings(PHPMD.UnusedFormalParameter)
     */
    public function before_loadEntities(
        Collection $subject,
        $printQuery = false,
        $logQuery = false
    ): array {
        $engine = $this->engineResolver->getCurrentSearchEngine();
        $pageSize = $subject->getPageSize();

        if ($pageSize && str_starts_with($engine, 'mysql') && $engine !== 'mysql') {
            $subject->getSelect()->reset(\Magento\Framework\DB\Select::LIMIT_COUNT);
            $subject->getSelect()->reset(\Magento\Framework\DB\Select::LIMIT_OFFSET);
            $subject->getSelect()->limitPage($subject->getCurPage(), $pageSize);
        }

        return [$printQuery, $logQuery];
    }
}
