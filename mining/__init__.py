from service import MiningService
from subscription import MiningSubscription

def setup():
    '''Setup mining service internal environment.
    You should not need to change this. If you
    want to use another Worker manager or Share manager,
    you should set proper reference to Interfaces class
    *before* you call setup() in the launcher script.'''
        
    from stratum import settings
    from interfaces import Interfaces
    
    from lib.block_updater import BlockUpdater
    from lib.template_registry import TemplateRegistry
    from lib.bitcoin_rpc import BitcoinRPC
    from lib.block_template import BlockTemplate
    from lib.coinbaser import SimpleCoinbaser
    
    bitcoin_rpc = BitcoinRPC(settings.BITCOIN_TRUSTED_HOST,
                             settings.BITCOIN_TRUSTED_PORT,
                             settings.BITCOIN_TRUSTED_USER,
                             settings.BITCOIN_TRUSTED_PASSWORD)
    
    registry = TemplateRegistry(BlockTemplate,
                                SimpleCoinbaser(bitcoin_rpc, settings.CENTRAL_WALLET),
                                bitcoin_rpc,
                                settings.INSTANCE_ID,
                                MiningSubscription.on_block)

    # Template registry is the main interface between Stratum service
    # and pool core logic
    Interfaces.set_template_registry(registry)
    
    # Set up polling mechanism for detecting new block on the network
    # This is just failsafe solution when -blocknotify
    # mechanism is not working properly    
    BlockUpdater(registry, bitcoin_rpc)