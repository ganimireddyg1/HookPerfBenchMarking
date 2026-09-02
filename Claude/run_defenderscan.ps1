trap { exit 0 }
 
$l = (
Get-ItemProperty `
-LiteralPath 'HKLM:\SOFTWARE\Microsoft\Windows Defender' `
-Name 'InstallLocation' `
-ErrorAction SilentlyContinue
).InstallLocation
 
if ($l) {
$p = Join-Path `
-Path $l `
-ChildPath 'DefenderAgentScan.exe'
 
if (Test-Path -LiteralPath $p) {
& $p
}
}
 
exit 0