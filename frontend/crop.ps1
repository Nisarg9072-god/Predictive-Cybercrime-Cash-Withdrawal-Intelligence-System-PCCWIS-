Add-Type -AssemblyName System.Drawing
$img = [System.Drawing.Image]::FromFile('C:\Users\Maitri\Desktop\cyber\Cyber-Craft-\frontend\src\assets\images\amrit_mahotsav_banner_80.jpg')
$rect = New-Object System.Drawing.Rectangle(0, 372, 1024, 280)
$bitmap = New-Object System.Drawing.Bitmap($img)
$cropped = $bitmap.Clone($rect, $bitmap.PixelFormat)
$cropped.Save('C:\Users\Maitri\Desktop\cyber\Cyber-Craft-\frontend\src\assets\images\amrit_mahotsav_banner_80_cropped.jpg', [System.Drawing.Imaging.ImageFormat]::Jpeg)
$img.Dispose()
$bitmap.Dispose()
$cropped.Dispose()
Write-Output "Image successfully cropped!"
