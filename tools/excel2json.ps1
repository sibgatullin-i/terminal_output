$file = read-host "Objects.xlsx filename [default: objects.xlxs]"
if ($file) { $excelFile = "$PSScriptRoot\$file" }
else { $excelFile = "$PSScriptRoot\objects.xlsx" }
$jsonFolder = "$PSScriptRoot\input"

Import-Module ImportExcel

Get-ChildItem $jsonFolder | Remove-Item

foreach ($object in (Import-Excel $excelFile )){
    $name = ($object.QUOTE_SET -replace "[^a-zA-Z0-9.-]") + '_' + ($object.QUOTE_NAME -replace "[^a-zA-Z0-9.-]")
    $object | convertto-json | Out-File -encoding oem -FilePath "$jsonFolder\$name.json"
}
