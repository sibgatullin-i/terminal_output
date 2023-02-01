#read settings
$settings = (get-content (Join-Path -Path $PSScriptRoot -ChildPath "settings.json") | ConvertFrom-json)

Import-Module ((join-path -path (join-path -Path $PSScriptRoot -ChildPath "tools") -ChildPath "source.psm1"))

$desiredLocation = $settings.desiredLocation
$interval = 300 #seconds

while ($true){
    while ((get-date) -lt (get-date -hour 18 -minute 59) -and (get-date) -gt (get-date -hour 09 -minute 00)){
        $locationCurrent = (Invoke-RestMethod -Method GET -Uri "http://ip-api.com/json/" -ErrorAction ignore).country
        Clear-Host
        write-host "$(get-date): current location is $locationCurrent`nDesired location is $desiredLocation"
        if ($locationCurrent -ne $desiredLocation){
            send-telegrammessage -tgToken $settins.tgToken -chatId $settings.chatId -text "Location is not $desiredLocation. Check VPN connection"
            [console]::beep(2500,2000)
        }
        start-sleep $interval
    }
start-sleep $interval
}