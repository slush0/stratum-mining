# Run me with "twistd -ny launcher_demo.tac"

# Add conf directory to python path.
# Configuration file is standard python module.
import os, sys
sys.path = [os.path.join(os.getcwd(), 'conf'),] + sys.path

# Bootstrap Stratum framework
import stratum
from stratum import settings
application = stratum.setup()

# Load mining service into stratum framework
import mining

from mining.interfaces import Interfaces
from mining.interfaces import WorkerManagerInterface, ShareManagerInterface, TimestamperInterface

Interfaces.set_share_manager(ShareManagerInterface())
Interfaces.set_worker_manager(WorkerManagerInterface())
Interfaces.set_timestamper(TimestamperInterface())

mining.setup()
