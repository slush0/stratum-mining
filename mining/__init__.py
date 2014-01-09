from service import MiningService
from subscription import MiningSubscription
from twisted.internet import defer
import time

@defer.inlineCallbacks
def setup(on_startup):
    '''Setup mining service internal environment.
    You should not need to change this. If you
    want to use another Worker manager or Share manager,
    you should set proper reference to Interfaces class
    *before* you call setup() in the launcher script.'''

    from stratum import settings
    from interfaces import Interfaces

    # Let's wait until share manager and worker manager boot up
    (yield Interfaces.share_manager.on_load)
    (yield Interfaces.worker_manager.on_load)

    from lib.block_updater import BlockUpdater
    from lib.template_registry import TemplateRegistry
    from lib.bitcoin_rpc import BitcoinRPC
    from lib.block_template import BlockTemplate
    from lib.coinbaser import SimpleCoinbaser

    bitcoin_rpc = BitcoinRPC(settings.BITCOIN_TRUSTED_HOST,
                             settings.BITCOIN_TRUSTED_PORT,
                             settings.BITCOIN_TRUSTED_USER,
                             settings.BITCOIN_TRUSTED_PASSWORD)

    import stratum.logger
    log = stratum.logger.get_logger('mining')

    log.info('Waiting for bitcoin RPC...')

    while True:
        try:
            result = (yield bitcoin_rpc.getblocktemplate())
            if isinstance(result, dict):
                log.info('Response from bitcoin RPC OK')
                break
        except:
            time.sleep(1)

    coinbaser = SimpleCoinbaser(bitcoin_rpc, settings.CENTRAL_WALLET)
    (yield coinbaser.on_load)

    registry = TemplateRegistry(BlockTemplate,
                                coinbaser,
                                bitcoin_rpc,
                                settings.INSTANCE_ID,
                                MiningSubscription.on_template,
                                Interfaces.share_manager.on_network_block)

    # Template registry is the main interface between Stratum service
    # and pool core logic
    Interfaces.set_template_registry(registry)

    # Set up polling mechanism for detecting new block on the network
    # This is just failsafe solution when -blocknotify
    # mechanism is not working properly
    BlockUpdater(registry, bitcoin_rpc)

    log.info("MINING SERVICE IS READY")
    on_startup.callback(True)
