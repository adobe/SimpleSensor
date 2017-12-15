# needs NSSM to install services, i use chocolatey to install that, its super handy
#Todo: detect and find paths to programs like python and node and dont hard code
#     remove the Aem screens bits so its just the sensor bits
Param($appDir)
Write-Host -ForeGroundColor Cyan "Setting up services"

#scripts path
$scriptpath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path $scriptpath
$sharedPath = $scriptDir + "\shared.ps1"
. $sharedPath

#setup collection point services
$serviceName = "CecFaceDetectCollectionPoint"
if (Get-Service $serviceName -ErrorAction SilentlyContinue){
    Write-Host "$serviceName service exists so all is good"
}else{
    $cmdArgs = 'install "'+$serviceName+'" "C:\Users\AEM\Anaconda3\python.exe"'
    Write-Host "command is = $cmdArgs"
    Start-Executable 'nssm' $cmdArgs
    $cmdArgs = 'set "'+$serviceName+'" AppDirectory '+$appDir+"cec_iot_sensor_base"
    Start-Executable 'nssm' $cmdArgs
    $cmdArgs = 'set "'+$serviceName+'" AppParameters main.py'
    Start-Executable 'nssm' $cmdArgs
}
