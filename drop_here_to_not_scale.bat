CD %~dp0
FOR %%A IN (%*) DO (
SET USEFILE=%%A
python rgb_converter.py %%A r g b
)
pause
