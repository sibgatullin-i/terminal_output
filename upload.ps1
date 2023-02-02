# v0.2 first prod
Import-Module posh-ssh

#read settings
$settings = (get-content (Join-Path -Path $PSScriptRoot -ChildPath "settings.json") | ConvertFrom-json)

Import-Module ((join-path -path (join-path -Path $PSScriptRoot -ChildPath "tools") -ChildPath "source.psm1"))

$credential = new-object System.Management.Automation.PSCredential($settings.sftpUsername, (ConvertTo-SecureString $settings.sftpPassword -AsPlaintext -Force) )

$sftpPath = $settings.sftpPath
$instanceName = $settings.instanceName

Clear-Host

# warn if Terminal is down
if ((Get-Process eikon).count -lt 1){
    $tgMessage = "$instanceName warning:`r`Terminal is not running"
    Send-TelegramMessage -tgToken $settings.tgToken -chatId $settings.chatId -text $tgMessage
    Write-Warning $tgMessage
    }

# check my ip and location
$myPublicIP = Invoke-RestMethod -Uri 'https://api.ipify.org'
$myLocation = (Invoke-RestMethod -Method GET -Uri "http://ip-api.com/json/$myPublicIP").country

#remove old output.csv if any
if ((Get-ChildItem $PSScriptRoot\tools\output.csv).count -gt 0) {
    remove-Item $PSScriptRoot\tools\output.csv
}

#launch terminal and look for output.csv, three times max
$terminalCounter = 3
while ($terminalCounter -ge 0) {
    & python.exe $PSScriptRoot\tools\output.py '..\input'
    if ((Get-ChildItem $PSScriptRoot\tools\output.csv).count -gt 0) {
        $terminalCounter = -1
    } else {
        --$terminalCounter
        start-Sleep 10
    }
}


#are we done?
if ((Get-ChildItem $PSScriptRoot\tools\output.csv).count -eq 0){
    Write-Warning "Failed to import data"
    Send-TelegramMessage -tgToken $settings.tgToken -chatId $settings.chatId -text "¯\_(ツ)_/¯`r`n$instancename`r`nfailed to import data"
    exit 1
}

$lastUpdate = (Get-ChildItem "$PSScriptRoot\tools\output.csv").LastWriteTime

# try to rename and CSV upload files
$sftp = (New-SFTPSession -computer $settings.sftpServer -Port $settings.sftpPort -Credential $credential)
if (!$sftp) {
    Write-Warning "Cannot establish SFTP connection"
    Send-TelegramMessage -tgToken $settings.tgToken -chatId $settings.chatId -text "¯\_(ツ)_/¯`r`n$instancename`r`nCannot connect to SFTP."
    exit
}

Get-ChildItem "$PSScriptRoot\tools\output.csv"| ForEach-Object {
    $newName = $PSScriptRoot + "\tools\" + $_.BaseName + "_" + (Get-Date -Format yyyyMMdd-HHmm) + $_.Extension
    Move-Item $_ $newName

    # calculate hash
    $newNameHash = (Get-FileHash -Algorithm SHA256 -Path $newName).Hash
    $newNameHashFile = "$PSScriptRoot\tools\" + (Get-ChildItem $newName).BaseName + ".sha256"
    Set-Content -Path "$newNameHashFile" -Encoding Ascii -Value $newNameHash
    
    Write-Host "$newname...uploading"    
        Set-SFTPItem -SFTPSession $sftp -Path $newName -Destination $sftpPath | Out-Null
        Set-SFTPItem -SFTPSession $sftp -Path $newNameHashFile -Destination $sftpPath | Out-Null
        $sftpFiles = (Get-SFTPChildItem -path $sftpPath -SFTPSession $sftp)
        if (
            (Get-ChildItem $newName).name -in $sftpFiles.name -and (Get-ChildItem $newNameHashFile).name -in $sftpFiles.name){
                Write-host ($sftpFiles | where-object -Property Name -eq (ls $newName).Name).fullname "...uploaded"
                Move-Item -Force $newName "$PSScriptRoot\archive\"
                Remove-Item -Force "$newNameHashFile"
                $tgMessage = "$instanceName`r`nupload successful`r`nIP is $myPublicIP`r`ngeolocation is $myLocation`r`nData update: $lastUpdate"
                Send-TelegramMessage -tgToken $settings.tgToken -chatId $settings.chatId -text $tgMessage
                Write-Host $tgMessage
                }else{
                    $_
                    $tgMessage = "$instanceName`r`nupload failed`r`nIP is $myPublicIP`r`ngeolocation is $myLocation`r`nData update: $lastUpdate"
                    Send-TelegramMessage -tgToken $settings.tgToken -chatId $settings.chatId -text $tgMessage
                    Write-Warning $tgMessage
                    exit
                    }
                }


Remove-SFTPSession $sftp.SessionId | Out-Null
Remove-Item $PSScriptRoot\tools\*.csv -Force | Out-Null

#check data is actually updated
if ((Get-Content -path ($PSScriptRoot + "\tools\lastprice")) -like "0"){
    Send-TelegramMessage -tgToken $settings.tgToken -chatId $settings.chatId -text "Warning`r`n$instanceName data seems to be not updated.`r`nPlease check!"
    Write-Warning "Calypso data seems to be not updated. Please check!"
}
