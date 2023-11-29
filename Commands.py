# Queue commands threadManager -> GUI
UPERROR = "UPDATEERROR"
UPLOG = "UPDATELOG"
UPJSON = "UPDATEJSON"

# Queue commands GUI -> threadManager
START = "START"
MUTE = "MUTE"
UNMUTE = "UNMUTE"
KILLTHREADS = "KILLTHREADS"

# Queue commands threadManager -> audioListener & transcriber
KILLSELF = "KILLSELF"

# Queue commands audioListener & transcriber -> threadManager
REPORTERROR = "REPORTERROR"
