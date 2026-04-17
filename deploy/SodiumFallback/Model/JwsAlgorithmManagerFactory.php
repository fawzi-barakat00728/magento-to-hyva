<?php
/**
 * Fallback for hosting environments where the sodium extension is unavailable
 * in the web SAPI (LiteSpeed/FPM), but enabled in CLI.
 */

declare(strict_types=1);

namespace MediaDivision\SodiumFallback\Model;

use Jose\Component\Core\AlgorithmManager;
use Jose\Component\Signature\Algorithm\EdDSA;
use Jose\Component\Signature\Algorithm\ES256;
use Jose\Component\Signature\Algorithm\ES384;
use Jose\Component\Signature\Algorithm\ES512;
use Jose\Component\Signature\Algorithm\HS256;
use Jose\Component\Signature\Algorithm\HS384;
use Jose\Component\Signature\Algorithm\HS512;
use Jose\Component\Signature\Algorithm\None;
use Jose\Component\Signature\Algorithm\PS256;
use Jose\Component\Signature\Algorithm\PS384;
use Jose\Component\Signature\Algorithm\PS512;
use Jose\Component\Signature\Algorithm\RS256;
use Jose\Component\Signature\Algorithm\RS384;
use Jose\Component\Signature\Algorithm\RS512;

class JwsAlgorithmManagerFactory extends \Magento\JwtFrameworkAdapter\Model\JwsAlgorithmManagerFactory
{
    public function create(): AlgorithmManager
    {
        $algorithms = [
            new HS256(),
            new HS384(),
            new HS512(),
            new RS256(),
            new RS384(),
            new RS512(),
            new PS256(),
            new PS384(),
            new PS512(),
            new ES256(),
            new ES384(),
            new ES512(),
        ];

        if (extension_loaded('sodium')) {
            $algorithms[] = new EdDSA();
        }

        $algorithms[] = new None();

        return new AlgorithmManager($algorithms);
    }
}
