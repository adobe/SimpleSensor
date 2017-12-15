#Install an msi and return a bool to say if it all went well or not.
function installMsi{
    param(
    $appDir,
    [Parameter(Mandatory=$true)][string]$name,
    [Parameter(Mandatory=$true)][string]$msiArgs,
    [Parameter(Mandatory=$false)][int]$timeOut=360)

    $logDirPath = $appDir + 'install_logs'
    checkMakeDir $logDirPath

    $resultSuccessful =$true
    
    try{
        $logFile = ' /L*V "' + $logDirPath + '\'+$name+'.log"'
        $callArgs = $msiArgs + $logFile
        Write-Host $callArgs
        $Timeoutms = $timeOut * 1000
        $ProcessStartInfo = New-Object System.Diagnostics.ProcessStartInfo
        $ProcessStartInfo.Filename = "msiexec"
        $ProcessStartInfo.Arguments = @($callArgs)
        $ProcessStartInfo.RedirectStandardError = $true
        $ProcessStartInfo.RedirectStandardOutput = $true
        $ProcessStartInfo.UseShellExecute = $false

        $Process = [System.Diagnostics.Process]::Start($ProcessStartInfo)
        $ProcessId = $Process.Id
        if(! $Process.WaitForExit($Timeoutms)){
            Write-Host "Killing $name on timeout"
            $Process.kill()
        }
        $output = $Process.StandardOutput.ReadToEnd()
        $output += $Process.StandardError.ReadToEnd()
        $logfilePath = $logDirPath +"\msi_install.log"
        $output | Out-File $logfilePath -Append
    }catch{
        $resultSuccessful =$false    
        showMsiError $name $_.Exception.Message $_.Exception.ItemName
    }
    
    return $resultSuccessful
}

function runGit{
    param(
    $appDir,
    [Parameter(Mandatory=$true)][string]$name,
    [Parameter(Mandatory=$true)][string]$gitArgs,
    [Parameter(Mandatory=$true)][string]$workDir,
    [Parameter(Mandatory=$false)][int]$timeOut=360)

    $logDirPath = $appDir + 'install_logs'
    checkMakeDir $logDirPath

    $resultSuccessful = 0
    
    try{
        $callArgs = $gitArgs
        $Timeoutms = $timeOut * 1000
        $ProcessStartInfo = New-Object System.Diagnostics.ProcessStartInfo
        $ProcessStartInfo.Filename = "git"
        $ProcessStartInfo.Arguments = @($callArgs)
        $ProcessStartInfo.RedirectStandardError = $true
        $ProcessStartInfo.RedirectStandardOutput = $true
        $ProcessStartInfo.UseShellExecute = $true
        $ProcessStartInfo.WorkingDirectory = $workDir

        $Process = [System.Diagnostics.Process]::Start($ProcessStartInfo)
        $ProcessId = $Process.Id
        if(! $Process.WaitForExit($Timeoutms)){
            Write-Host "Killing GIT $name on timeout"
            $Process.kill()
        }
        $output = $Process.StandardOutput.ReadToEnd()
        $output += $Process.StandardError.ReadToEnd()
        $logfilePath = $logDirPath +"\git_command.log"
        $output | Out-File $logfilePath -Append
        $resultSuccessful = $Process.ExitCode
    }catch{
        $resultSuccessful = $Process.ExitCode    
        showGitError $name $_.Exception.Message $_.Exception.ItemName
    }
    
    return $resultSuccessful
}

function showGitError{
    param([string]$Name,[string]$ErrorMessage,[string]$FailedItem )

    Write-Host -ForeGroundColor red "Danng, something went wrong pulling code from GIT. I blame Mark."
    Write-Host -ForeGroundColor red "Name: $Name"
    Write-Host -ForeGroundColor red "Item name: $FailedItem"
    Write-Host -ForeGroundColor red "Error message: $ErrorMessage"
}

function showMsiError{
    param([string]$Name,[string]$ErrorMessage,[string]$FailedItem )

    Write-Host -ForeGroundColor red "Danng, something went wrong installing an MSI. I blame Mark."
    Write-Host -ForeGroundColor red "Name: $Name"
    Write-Host -ForeGroundColor red "Item name: $FailedItem"
    Write-Host -ForeGroundColor red "Error message: $ErrorMessage"
}

function checkMakeDir{
    param([Parameter(Mandatory=$true)][string]$dirPath)
    
    if(!(Test-Path $dirPath)){
        Write-Host -ForeGroundColor yellow "Directory missing. Creating directory $dirPath"
        New-Item -ItemType directory -Path $dirPath -Force
    }else{
        Write-Host -ForeGroundColor green "Directory $dirPath exists so we are going to do my favorite thing, nothing. "
    }
}

function Start-Executable {
  param(
    [String] $FilePath,
    [String[]] $ArgumentList
  )
  $OFS = " "
  $process = New-Object System.Diagnostics.Process
  $process.StartInfo.FileName = $FilePath
  $process.StartInfo.Arguments = $ArgumentList
  $process.StartInfo.UseShellExecute = $false
  $process.StartInfo.RedirectStandardOutput = $true
  if ( $process.Start() ) {
    $output = $process.StandardOutput.ReadToEnd() `
      -replace "\r\n$",""
    if ( $output ) {
      if ( $output.Contains("`r`n") ) {
        $output -split "`r`n"
      }
      elseif ( $output.Contains("`n") ) {
        $output -split "`n"
      }
      else {
        $output
      }
    }
    $process.WaitForExit()
    & "$Env:SystemRoot\system32\cmd.exe" `
      /c exit $process.ExitCode
  }

  return $output
}

function which{
    param(
        [String] $name
      )
    Get-Command $name | Select-Object -ExpandProperty Definition
}