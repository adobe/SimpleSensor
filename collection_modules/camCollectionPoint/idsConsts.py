# TODO: formalize these constants
"""
AOI HEX CODES
"""
IS_AOI_IMAGE_SET_AOI = 0x0001
IS_AOI_IMAGE_GET_AOI=0x0002
IS_AOI_IMAGE_SET_POS=0x0003
IS_AOI_IMAGE_GET_POS=0x0004
IS_AOI_IMAGE_SET_SIZE=0x0005
IS_AOI_IMAGE_GET_SIZE=0x0006
IS_AOI_IMAGE_GET_POS_MIN=0x0007
IS_AOI_IMAGE_GET_SIZE_MIN=0x0008
IS_AOI_IMAGE_GET_POS_MAX=0x0009
IS_AOI_IMAGE_GET_SIZE_MAX=0x0010
IS_AOI_IMAGE_GET_POS_INC=0x0011
IS_AOI_IMAGE_GET_SIZE_INC=0x0012
IS_AOI_IMAGE_GET_POS_X_ABS=0x0013
IS_AOI_IMAGE_GET_POS_Y_ABS=0x0014
IS_AOI_IMAGE_GET_ORIGINAL_AOI=0x0015

"""
COLOR MODES
"""
IS_CM_SENSOR_RAW8 = 11
IS_CM_SENSOR_RAW10 = 33
IS_CM_SENSOR_RAW12 = 27
IS_CM_SENSOR_RAW16 = 29
IS_CM_MONO8=6

"""
MISC CONSTS
"""
INT_BYTE_SIZE = 4

"""
DISPLAY MODE SELECTORS
"""
IS_GET_DISPLAY_MODE=0x8000
IS_SET_DM_DIB=1
IS_SET_DM_DIRECT3D=4
IS_SET_DM_OPENGL=8
IS_SET_DM_MONO=0x800
IS_SET_DM_BAYER=0x1000
IS_SET_DM_YCBCR=0x4000

"""
IMAGE FORMAT COMMANDS
"""
IMGFRMT_CMD_GET_NUM_ENTRIES= 1,  """Get the number of supported image formats.
                                    pParam hast to be a Pointer to IS_U32. If  -1 is reported, the device
                                    supports continuous AOI settings (maybe with fixed increments)"""
IMGFRMT_CMD_GET_LIST= 2  #Get a array of IMAGE_FORMAT_ELEMENTs.
IMGFRMT_CMD_SET_FORMAT= 3  #Select a image format
IMGFRMT_CMD_GET_ARBITRARY_AOI_SUPPORTED= 4  #Does the device supports the setting of an arbitrary AOI.
IMGFRMT_CMD_GET_FORMAT_INFO= 5

"""
CODES FOR UEYE XS FORMATS
"""
FIVE_MP = 4 #2592 x 1944 5MP
THREE_MP = 5 #2048 x 1536 3MP
FHD = 6 #1920 x 1080 Full HD 16:9
ONE_POINT_TWO_MP = 8 #1280 x 960 1.2M 4:3
HIGH_DEF = 9 #1280 x 720 HD 16:9
WVGA = 12 #800 x 480 WVGA
VGA = 13 #640 x 480 VGA
UXGA = 20 #1600 x 1200 UXGA

IS_DONT_WAIT  = 0x0000
IS_GET_LIVE = 0x8000
IS_SET_TRIGGER_SOFTWARE = 0x1000

"""
ERROR CODES
"""
IS_NO_SUCCESS                        =-1   #function call failed
IS_SUCCESS                            =0   #function call succeeded
IS_INVALID_CAMERA_HANDLE              =1   #camera handle is not valid or zero
IS_INVALID_HANDLE                     =1   #a handle other than the camera handle is invalid

IS_IO_REQUEST_FAILED                  =2   #an io request to the driver failed
IS_CANT_OPEN_DEVICE                   =3   #returned by is_InitCamera
IS_CANT_CLOSE_DEVICE                  =4
IS_CANT_SETUP_MEMORY                  =5
IS_NO_HWND_FOR_ERROR_REPORT           =6
IS_ERROR_MESSAGE_NOT_CREATED          =7
IS_ERROR_STRING_NOT_FOUND             =8
IS_HOOK_NOT_CREATED                   =9
IS_TIMER_NOT_CREATED                 =10
IS_CANT_OPEN_REGISTRY                =11
IS_CANT_READ_REGISTRY                =12
IS_CANT_VALIDATE_BOARD               =13
IS_CANT_GIVE_BOARD_ACCESS            =14
IS_NO_IMAGE_MEM_ALLOCATED            =15
IS_CANT_CLEANUP_MEMORY               =16
IS_CANT_COMMUNICATE_WITH_DRIVER      =17
IS_FUNCTION_NOT_SUPPORTED_YET        =18
IS_OPERATING_SYSTEM_NOT_SUPPORTED    =19

IS_INVALID_VIDEO_IN                  =20
IS_INVALID_IMG_SIZE                  =21
IS_INVALID_ADDRESS                   =22
IS_INVALID_VIDEO_MODE                =23
IS_INVALID_AGC_MODE                  =24
IS_INVALID_GAMMA_MODE                =25
IS_INVALID_SYNC_LEVEL                =26
IS_INVALID_CBARS_MODE                =27
IS_INVALID_COLOR_MODE                =28
IS_INVALID_SCALE_FACTOR              =29
IS_INVALID_IMAGE_SIZE                =30
IS_INVALID_IMAGE_POS                 =31
IS_INVALID_CAPTURE_MODE              =32
IS_INVALID_RISC_PROGRAM              =33
IS_INVALID_BRIGHTNESS                =34
IS_INVALID_CONTRAST                  =35
IS_INVALID_SATURATION_U              =36
IS_INVALID_SATURATION_V              =37
IS_INVALID_HUE                       =38
IS_INVALID_HOR_FILTER_STEP           =39
IS_INVALID_VERT_FILTER_STEP          =40
IS_INVALID_EEPROM_READ_ADDRESS       =41
IS_INVALID_EEPROM_WRITE_ADDRESS      =42
IS_INVALID_EEPROM_READ_LENGTH        =43
IS_INVALID_EEPROM_WRITE_LENGTH       =44
IS_INVALID_BOARD_INFO_POINTER        =45
IS_INVALID_DISPLAY_MODE              =46
IS_INVALID_ERR_REP_MODE              =47
IS_INVALID_BITS_PIXEL                =48
IS_INVALID_MEMORY_POINTER            =49

IS_FILE_WRITE_OPEN_ERROR             =50
IS_FILE_READ_OPEN_ERROR              =51
IS_FILE_READ_INVALID_BMP_ID          =52
IS_FILE_READ_INVALID_BMP_SIZE        =53
IS_FILE_READ_INVALID_BIT_COUNT       =54
IS_WRONG_KERNEL_VERSION              =55

IS_RISC_INVALID_XLENGTH              =60
IS_RISC_INVALID_YLENGTH              =61
IS_RISC_EXCEED_IMG_SIZE              =62

# DirectDraw Mode errors
IS_DD_MAIN_FAILED                    =70
IS_DD_PRIMSURFACE_FAILED             =71
IS_DD_SCRN_SIZE_NOT_SUPPORTED        =72
IS_DD_CLIPPER_FAILED                 =73
IS_DD_CLIPPER_HWND_FAILED            =74
IS_DD_CLIPPER_CONNECT_FAILED         =75
IS_DD_BACKSURFACE_FAILED             =76
IS_DD_BACKSURFACE_IN_SYSMEM          =77
IS_DD_MDL_MALLOC_ERR                 =78
IS_DD_MDL_SIZE_ERR                   =79
IS_DD_CLIP_NO_CHANGE                 =80
IS_DD_PRIMMEM_NULL                   =81
IS_DD_BACKMEM_NULL                   =82
IS_DD_BACKOVLMEM_NULL                =83
IS_DD_OVERLAYSURFACE_FAILED          =84
IS_DD_OVERLAYSURFACE_IN_SYSMEM       =85
IS_DD_OVERLAY_NOT_ALLOWED            =86
IS_DD_OVERLAY_COLKEY_ERR             =87
IS_DD_OVERLAY_NOT_ENABLED            =88
IS_DD_GET_DC_ERROR                   =89
IS_DD_DDRAW_DLL_NOT_LOADED           =90
IS_DD_THREAD_NOT_CREATED             =91
IS_DD_CANT_GET_CAPS                  =92
IS_DD_NO_OVERLAYSURFACE              =93
IS_DD_NO_OVERLAYSTRETCH              =94
IS_DD_CANT_CREATE_OVERLAYSURFACE     =95
IS_DD_CANT_UPDATE_OVERLAYSURFACE     =96
IS_DD_INVALID_STRETCH                =97

IS_EV_INVALID_EVENT_NUMBER          =100
IS_INVALID_MODE                     =101
IS_CANT_FIND_FALCHOOK               =102
IS_CANT_FIND_HOOK                   =102
IS_CANT_GET_HOOK_PROC_ADDR          =103
IS_CANT_CHAIN_HOOK_PROC             =104
IS_CANT_SETUP_WND_PROC              =105
IS_HWND_NULL                        =106
IS_INVALID_UPDATE_MODE              =107
IS_NO_ACTIVE_IMG_MEM                =108
IS_CANT_INIT_EVENT                  =109
IS_FUNC_NOT_AVAIL_IN_OS             =110
IS_CAMERA_NOT_CONNECTED             =111
IS_SEQUENCE_LIST_EMPTY              =112
IS_CANT_ADD_TO_SEQUENCE             =113
IS_LOW_OF_SEQUENCE_RISC_MEM         =114
IS_IMGMEM2FREE_USED_IN_SEQ          =115
IS_IMGMEM_NOT_IN_SEQUENCE_LIST      =116
IS_SEQUENCE_BUF_ALREADY_LOCKED      =117
IS_INVALID_DEVICE_ID                =118
IS_INVALID_BOARD_ID                 =119
IS_ALL_DEVICES_BUSY                 =120
IS_HOOK_BUSY                        =121
IS_TIMED_OUT                        =122
IS_NULL_POINTER                     =123
IS_WRONG_HOOK_VERSION               =124
IS_INVALID_PARAMETER                =125   # a parameter specified was invalid
IS_NOT_ALLOWED                      =126
IS_OUT_OF_MEMORY                    =127
IS_INVALID_WHILE_LIVE               =128
IS_ACCESS_VIOLATION                 =129   # an internal exception occurred
IS_UNKNOWN_ROP_EFFECT               =130
IS_INVALID_RENDER_MODE              =131
IS_INVALID_THREAD_CONTEXT           =132
IS_NO_HARDWARE_INSTALLED            =133
IS_INVALID_WATCHDOG_TIME            =134
IS_INVALID_WATCHDOG_MODE            =135
IS_INVALID_PASSTHROUGH_IN           =136
IS_ERROR_SETTING_PASSTHROUGH_IN     =137
IS_FAILURE_ON_SETTING_WATCHDOG      =138
IS_NO_USB20                         =139   # the usb port doesnt support usb 2.0
IS_CAPTURE_RUNNING                  =140   # there is already a capture running

IS_MEMORY_BOARD_ACTIVATED           =141   # operation could not execute while mboard is enabled
IS_MEMORY_BOARD_DEACTIVATED         =142   # operation could not execute while mboard is disabled
IS_NO_MEMORY_BOARD_CONNECTED        =143   # no memory board connected
IS_TOO_LESS_MEMORY                  =144   # image size is above memory capacity
IS_IMAGE_NOT_PRESENT                =145   # requested image is no longer present in the camera
IS_MEMORY_MODE_RUNNING              =146
IS_MEMORYBOARD_DISABLED             =147

IS_TRIGGER_ACTIVATED                =148   # operation could not execute while trigger is enabled
IS_WRONG_KEY                        =150
IS_CRC_ERROR                        =151
IS_NOT_YET_RELEASED                 =152   # this feature is not available yet
IS_NOT_CALIBRATED                   =153   # the camera is not calibrated
IS_WAITING_FOR_KERNEL               =154   # a request to the kernel exceeded
IS_NOT_SUPPORTED                    =155   # operation mode is not supported
IS_TRIGGER_NOT_ACTIVATED            =156   # operation could not execute while trigger is disabled
IS_OPERATION_ABORTED                =157
IS_BAD_STRUCTURE_SIZE               =158
IS_INVALID_BUFFER_SIZE              =159
IS_INVALID_PIXEL_CLOCK              =160
IS_INVALID_EXPOSURE_TIME            =161
IS_AUTO_EXPOSURE_RUNNING            =162
IS_CANNOT_CREATE_BB_SURF            =163   # error creating backbuffer surface  
IS_CANNOT_CREATE_BB_MIX             =164   # backbuffer mixer surfaces can not be created
IS_BB_OVLMEM_NULL                   =165   # backbuffer overlay mem could not be locked  
IS_CANNOT_CREATE_BB_OVL             =166   # backbuffer overlay mem could not be created  
IS_NOT_SUPP_IN_OVL_SURF_MODE        =167   # function not supported in overlay surface mode  
IS_INVALID_SURFACE                  =168   # surface invalid
IS_SURFACE_LOST                     =169   # surface has been lost  
IS_RELEASE_BB_OVL_DC                =170   # error releasing backbuffer overlay DC  
IS_BB_TIMER_NOT_CREATED             =171   # backbuffer timer could not be created  
IS_BB_OVL_NOT_EN                    =172   # backbuffer overlay has not been enabled  
IS_ONLY_IN_BB_MODE                  =173   # only possible in backbuffer mode 
IS_INVALID_COLOR_FORMAT             =174   # invalid color format
IS_INVALID_WB_BINNING_MODE          =175   # invalid binning mode for AWB 
IS_INVALID_I2C_DEVICE_ADDRESS       =176   # invalid I2C device address
IS_COULD_NOT_CONVERT                =177   # current image couldn't be converted
IS_TRANSFER_ERROR                   =178   # transfer failed
IS_PARAMETER_SET_NOT_PRESENT        =179   # the parameter set is not present
IS_INVALID_CAMERA_TYPE              =180   # the camera type in the ini file doesn't match
IS_INVALID_HOST_IP_HIBYTE           =181   # HIBYTE of host address is invalid
IS_CM_NOT_SUPP_IN_CURR_DISPLAYMODE  =182   # color mode is not supported in the current display mode
IS_NO_IR_FILTER                     =183
IS_STARTER_FW_UPLOAD_NEEDED         =184   # device starter firmware is not compatible    

IS_DR_LIBRARY_NOT_FOUND                     =185   # the DirectRender library could not be found
IS_DR_DEVICE_OUT_OF_MEMORY                  =186   # insufficient graphics adapter video memory
IS_DR_CANNOT_CREATE_SURFACE                 =187   # the image or overlay surface could not be created
IS_DR_CANNOT_CREATE_VERTEX_BUFFER           =188   # the vertex buffer could not be created
IS_DR_CANNOT_CREATE_TEXTURE                 =189   # the texture could not be created  
IS_DR_CANNOT_LOCK_OVERLAY_SURFACE           =190   # the overlay surface could not be locked
IS_DR_CANNOT_UNLOCK_OVERLAY_SURFACE         =191   # the overlay surface could not be unlocked
IS_DR_CANNOT_GET_OVERLAY_DC                 =192   # cannot get the overlay surface DC 
IS_DR_CANNOT_RELEASE_OVERLAY_DC             =193   # cannot release the overlay surface DC
IS_DR_DEVICE_CAPS_INSUFFICIENT              =194   # insufficient graphics adapter capabilities
IS_INCOMPATIBLE_SETTING                     =195   # Operation is not possible because of another incompatible setting
IS_DR_NOT_ALLOWED_WHILE_DC_IS_ACTIVE        =196   # user App still has DC handle.
IS_DEVICE_ALREADY_PAIRED                    =197   # The device is already paired
IS_SUBNETMASK_MISMATCH                      =198   # The subnetmasks of the device and the adapter differ
IS_SUBNET_MISMATCH                          =199   # The subnets of the device and the adapter differ
IS_INVALID_IP_CONFIGURATION                 =200   # The IP configuation of the device is invalid
IS_DEVICE_NOT_COMPATIBLE                    =201   # The device is incompatible to the driver
IS_NETWORK_FRAME_SIZE_INCOMPATIBLE          =202   # The frame size settings of the device and the network adapter are incompatible
IS_NETWORK_CONFIGURATION_INVALID            =203   # The network adapter configuration is invalid
IS_ERROR_CPU_IDLE_STATES_CONFIGURATION      =204   # The setting of the CPU idle state configuration failed
IS_DEVICE_BUSY                              =205   # The device is busy. The operation must be executed again later.
IS_SENSOR_INITIALIZATION_FAILED             =206   # The sensor initialization failed


'''
DEVICE FEATURE CMDS
'''

IS_DEVICE_FEATURE_CMD_GET_SUPPORTED_FEATURES= 1
IS_DEVICE_FEATURE_CMD_SET_LINESCAN_MODE= 2
IS_DEVICE_FEATURE_CMD_GET_LINESCAN_MODE= 3
IS_DEVICE_FEATURE_CMD_SET_LINESCAN_NUMBER= 4
IS_DEVICE_FEATURE_CMD_GET_LINESCAN_NUMBER= 5
IS_DEVICE_FEATURE_CMD_SET_SHUTTER_MODE= 6
IS_DEVICE_FEATURE_CMD_GET_SHUTTER_MODE= 7
IS_DEVICE_FEATURE_CMD_SET_PREFER_XS_HS_MODE= 8
IS_DEVICE_FEATURE_CMD_GET_PREFER_XS_HS_MODE= 9
IS_DEVICE_FEATURE_CMD_GET_DEFAULT_PREFER_XS_HS_MODE= 10
IS_DEVICE_FEATURE_CMD_GET_LOG_MODE_DEFAULT= 11
IS_DEVICE_FEATURE_CMD_GET_LOG_MODE= 12
IS_DEVICE_FEATURE_CMD_SET_LOG_MODE= 13
IS_DEVICE_FEATURE_CMD_GET_LOG_MODE_MANUAL_VALUE_DEFAULT= 14
IS_DEVICE_FEATURE_CMD_GET_LOG_MODE_MANUAL_VALUE_RANGE= 15
IS_DEVICE_FEATURE_CMD_GET_LOG_MODE_MANUAL_VALUE= 16
IS_DEVICE_FEATURE_CMD_SET_LOG_MODE_MANUAL_VALUE= 17
IS_DEVICE_FEATURE_CMD_GET_LOG_MODE_MANUAL_GAIN_DEFAULT= 18
IS_DEVICE_FEATURE_CMD_GET_LOG_MODE_MANUAL_GAIN_RANGE= 19
IS_DEVICE_FEATURE_CMD_GET_LOG_MODE_MANUAL_GAIN= 20
IS_DEVICE_FEATURE_CMD_SET_LOG_MODE_MANUAL_GAIN= 21
IS_DEVICE_FEATURE_CMD_GET_VERTICAL_AOI_MERGE_MODE_DEFAULT= 22
IS_DEVICE_FEATURE_CMD_GET_VERTICAL_AOI_MERGE_MODE= 23
IS_DEVICE_FEATURE_CMD_SET_VERTICAL_AOI_MERGE_MODE= 24
IS_DEVICE_FEATURE_CMD_GET_VERTICAL_AOI_MERGE_POSITION_DEFAULT= 25
IS_DEVICE_FEATURE_CMD_GET_VERTICAL_AOI_MERGE_POSITION_RANGE= 26
IS_DEVICE_FEATURE_CMD_GET_VERTICAL_AOI_MERGE_POSITION= 27
IS_DEVICE_FEATURE_CMD_SET_VERTICAL_AOI_MERGE_POSITION= 28
IS_DEVICE_FEATURE_CMD_GET_FPN_CORRECTION_MODE_DEFAULT= 29
IS_DEVICE_FEATURE_CMD_GET_FPN_CORRECTION_MODE= 30
IS_DEVICE_FEATURE_CMD_SET_FPN_CORRECTION_MODE= 31
IS_DEVICE_FEATURE_CMD_GET_SENSOR_SOURCE_GAIN_RANGE= 32
IS_DEVICE_FEATURE_CMD_GET_SENSOR_SOURCE_GAIN_DEFAULT= 33
IS_DEVICE_FEATURE_CMD_GET_SENSOR_SOURCE_GAIN= 34
IS_DEVICE_FEATURE_CMD_SET_SENSOR_SOURCE_GAIN= 35
IS_DEVICE_FEATURE_CMD_GET_BLACK_REFERENCE_MODE_DEFAULT= 36
IS_DEVICE_FEATURE_CMD_GET_BLACK_REFERENCE_MODE= 37
IS_DEVICE_FEATURE_CMD_SET_BLACK_REFERENCE_MODE= 38
IS_DEVICE_FEATURE_CMD_GET_ALLOW_RAW_WITH_LUT= 39
IS_DEVICE_FEATURE_CMD_SET_ALLOW_RAW_WITH_LUT= 40
IS_DEVICE_FEATURE_CMD_GET_SUPPORTED_SENSOR_BIT_DEPTHS= 41
IS_DEVICE_FEATURE_CMD_GET_SENSOR_BIT_DEPTH_DEFAULT= 42
IS_DEVICE_FEATURE_CMD_GET_SENSOR_BIT_DEPTH= 43
IS_DEVICE_FEATURE_CMD_SET_SENSOR_BIT_DEPTH= 44
IS_DEVICE_FEATURE_CMD_GET_TEMPERATURE= 45
IS_DEVICE_FEATURE_CMD_GET_JPEG_COMPRESSION= 46
IS_DEVICE_FEATURE_CMD_SET_JPEG_COMPRESSION= 47
IS_DEVICE_FEATURE_CMD_GET_JPEG_COMPRESSION_DEFAULT= 48
IS_DEVICE_FEATURE_CMD_GET_JPEG_COMPRESSION_RANGE= 49
IS_DEVICE_FEATURE_CMD_GET_NOISE_REDUCTION_MODE= 50
IS_DEVICE_FEATURE_CMD_SET_NOISE_REDUCTION_MODE= 51
IS_DEVICE_FEATURE_CMD_GET_NOISE_REDUCTION_MODE_DEFAULT= 52
IS_DEVICE_FEATURE_CMD_GET_TIMESTAMP_CONFIGURATION= 53
IS_DEVICE_FEATURE_CMD_SET_TIMESTAMP_CONFIGURATION= 54
IS_DEVICE_FEATURE_CMD_GET_VERTICAL_AOI_MERGE_HEIGHT_DEFAULT= 55
IS_DEVICE_FEATURE_CMD_GET_VERTICAL_AOI_MERGE_HEIGHT_NUMBER= 56
IS_DEVICE_FEATURE_CMD_GET_VERTICAL_AOI_MERGE_HEIGHT_LIST= 57
IS_DEVICE_FEATURE_CMD_GET_VERTICAL_AOI_MERGE_HEIGHT= 58
IS_DEVICE_FEATURE_CMD_SET_VERTICAL_AOI_MERGE_HEIGHT= 59
IS_DEVICE_FEATURE_CMD_GET_VERTICAL_AOI_MERGE_ADDITIONAL_POSITION_DEFAULT= 60
IS_DEVICE_FEATURE_CMD_GET_VERTICAL_AOI_MERGE_ADDITIONAL_POSITION_RANGE= 61
IS_DEVICE_FEATURE_CMD_GET_VERTICAL_AOI_MERGE_ADDITIONAL_POSITION= 62
IS_DEVICE_FEATURE_CMD_SET_VERTICAL_AOI_MERGE_ADDITIONAL_POSITION= 63
IS_DEVICE_FEATURE_CMD_GET_SENSOR_TEMPERATURE_NUMERICAL_VALUE= 64
IS_DEVICE_FEATURE_CMD_SET_IMAGE_EFFECT= 65
IS_DEVICE_FEATURE_CMD_GET_IMAGE_EFFECT= 66
IS_DEVICE_FEATURE_CMD_GET_IMAGE_EFFECT_DEFAULT= 67
IS_DEVICE_FEATURE_CMD_GET_EXTENDED_PIXELCLOCK_RANGE_ENABLE_DEFAULT= 68
IS_DEVICE_FEATURE_CMD_GET_EXTENDED_PIXELCLOCK_RANGE_ENABLE= 69
IS_DEVICE_FEATURE_CMD_SET_EXTENDED_PIXELCLOCK_RANGE_ENABLE= 70
IS_DEVICE_FEATURE_CMD_MULTI_INTEGRATION_GET_SCOPE= 71
IS_DEVICE_FEATURE_CMD_MULTI_INTEGRATION_GET_PARAMS= 72
IS_DEVICE_FEATURE_CMD_MULTI_INTEGRATION_SET_PARAMS= 73
IS_DEVICE_FEATURE_CMD_MULTI_INTEGRATION_GET_MODE_DEFAULT= 74
IS_DEVICE_FEATURE_CMD_MULTI_INTEGRATION_GET_MODE= 75
IS_DEVICE_FEATURE_CMD_MULTI_INTEGRATION_SET_MODE= 76
IS_DEVICE_FEATURE_CMD_SET_I2C_TARGET= 77


'''
PIXEL CLOCK CONSTS
'''

IS_PIXELCLOCK_CMD_GET_NUMBER    = 1
IS_PIXELCLOCK_CMD_GET_LIST      = 2
IS_PIXELCLOCK_CMD_GET_RANGE     = 3
IS_PIXELCLOCK_CMD_GET_DEFAULT   = 4
IS_PIXELCLOCK_CMD_GET           = 5
IS_PIXELCLOCK_CMD_SET           = 6