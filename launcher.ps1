#read settings
$settings = (get-content (Join-Path -Path $PSScriptRoot -ChildPath "settings.json") | ConvertFrom-json)

$workFromHours = $settings.workFromHours
$workFromMinutes = $settings.workFromMinutes
$workToHours = $settings.workToHours
$workToMinutes = $settings.workToMinutes
$intervalRun = $settings.intervalRun #minutes
$intervalCheck = $settings.intervalCheck #seconds

$host.ui.RawUI.WindowTitle = "output Launcher"

$testTerminalNow = $true
$testGeolocationNow = ""
function Check-Apps {
    $timeNow = ((get-date).tostring("HH:mm"))
    #test Terminal
    $Global:testTerminalPrev = $Global:testTerminalNow
    if ((Get-Process | Where-Object -Property ProcessName -eq "eikon").count -eq 0){
        $Global:testTerminalNow = $false
        }else{
            $Global:testTerminalNow = $true
            }        
    #test geolocation
    $Global:testGeolocationPrev = $Global:testGeolocationNow
    try {$Global:testGeolocationNow = (Invoke-RestMethod -Method GET -Uri "http://ip-api.com/json/" -ErrorAction ignore).country}
    catch {[console]::beep(2500,2000)}
    if (!$Global:testGeolocationNow){$Global:testGeolocationNow = "NO INTERNET CONNECTION!!!"}
    #show status   
    if ($Global:testTerminalPrev -ne $Global:testTerminalNow -and $Global:testTerminalNow -eq $true){
        Write-Host "$timeNow`: Terminal is up"
        }
    if ($Global:testTerminalPrev -ne $Global:testTerminalNow -and $Global:testTerminalNow -eq $false){
        Write-Warning "$timeNow`: Terminal is down"
        }
    if ($Global:testGeolocationPrev -ne $Global:testGeolocationNow){
        Write-Host "$timeNow`: IP geolocation is $Global:testGeolocationNow"
    }
    }
    

while ($true){
    while ((get-date) -gt (get-date -hour $workFromHours -Minute $workFromMinutes -Second 0) -and (get-date) -lt (get-date -Hour $workToHours -Minute $workToMinutes -Second 0)){
        $lastStart = (get-date)
        & "$PSScriptRoot\upload.ps1"
        $lastRun = ((get-date) - $lastStart)
        Write-Host "Done in: " $lastRun.ToString("mm' min 'ss' seconds'")
        if ($lastStart.AddMinutes($intervalRun) -lt (get-date -Hour $workToHours -Minute $workToMinutes -Second 0)){
            Write-Host "Next run at" $lastStart.AddMinutes($intervalRun).ToString("HH:mm")
            } else { break }
        write-host "Running until" (get-date -Hour $workToHours -Minute $workToMinutes).ToString("HH:mm")
        $timer = [math]::Round((($intervalRun * 60) - $lastRun.TotalSeconds))
        while ($timer -gt $intervalCheck){
            $timer = $timer - $intervalCheck
            $t1 = (get-date)
            Check-Apps
            $t2 = [math]::Round(((get-date) - $t1).totalseconds)
            if (($intervalCheck - $t2) -gt 0){
                Start-Sleep ($intervalCheck - $t2)
            }
        }
        Clear-Host
        }
    if ( ((get-date -Hour $workFromHours -Minute $workFromMinutes) - (get-date)).totalseconds -ge 0) {
    $nextRunAt = (get-date -hour $workFromHours -Minute $workFromMinutes)
    $nextRunIn = [math]::Round(($nextRunAt - (get-date)).totalseconds)
    }else{
        $nextRunAt = (get-date -hour $workFromHours -Minute $workFromMinutes).adddays(1)
        $nextRunIn = [math]::Round(($nextRunAt - (get-date)).totalseconds)
        }
    write-host "Out of timeframe, sleeping until" $nextRunAt.ToString("dd MMMM HH:mm")
    while ($nextRunIn -gt 0){
        $nextRunIn = $nextRunIn - $intervalCheck
        $t1 = (get-date)
        Check-Apps
        $t2 = [math]::Round(((get-date) - $t1).totalseconds)
        if (($intervalCheck - $t2) -gt 0){
            Start-Sleep ($intervalCheck - $t2)
        }
    }
}
