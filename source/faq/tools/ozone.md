# 4 Ozone相关
## 4.1 Ozone debug连接不成功，
提示:<br>
![alt text](./assets/ozone001.png)<br>   
你需要按照jlink一样，添加好flash的驱动和xml配置文件， 这样Ozone才支持SF32LB55X芯片.<br>
```
C:\Program Files\SEGGER\Ozone\Devices\SiFli\SF32LB55X****.elf
C:\Program Files\SEGGER\Ozone\JLinkDevices.xml
```
## 4.2 Ozone或者keil如何单步debug Lcpu
1， jlink默认connect会连接到hcpu,可以直接debug Hcpu，如果要debug Lcpu，可以在windows cmd命令窗口执行SDK\tools\segger\jlink_lcpu_a0.bat， 执行该批处理，其实执行的是\tools\segger\jlink_lcpu_a0.jlink里面的几条命令:<br>
```
w4 0x4004f000 1
connect
w4 0x40070000 0 
exit
```
也可以直接在jlink窗口依次输入这两条命令，切换到lcpu.<br>
![alt text](./assets/ozone002.png)<br>   
2， 现在以Ozone为例，演示Lcpu单步运行， 先创建一个新项目<br>
![alt text](./assets/ozone003.png)<br>    
3， 选择调试芯片，
如果找不到，需要在
C:\Program Files\SEGGER\Ozone\JLinkDevices.xml 添加55x芯片型号配置
和C:\Program Files\SEGGER\Ozone\Devices\SiFli\SF32LB55X_******.elf  四个flash烧录文件<br>
![alt text](./assets/ozone004.png)<br>    
4， 选择已经连接PC的jlink器件， 如果找不到，检查jlink连接和jlink供电<br>
5， 选择你编译出来的lcpu的*.axf文件，如果是watch_demo工程，路径会在
```
\release\example\rom_bin\lcpu_general_ble_img\lcpu_general_551.axf
```
![alt text](./assets/ozone005.png)<br>    
6，下一步都选择Do no set选项， finish完成<br>
![alt text](./assets/ozone006.png)<br>    
7， Attach并且halt Program 就是让jlink连接到lcpu，并停在当前运行的PC指针，
Attch并且Running Program就是让jlink连接到lcpu，并且开始从当前PC继续运行程序，<br>
![alt text](./assets/ozone007.png)<br>    
8，点击运行程序箭头图标后， 可以看到lcpu已经可以单步运行，并且添加断点，查看栈信息和寄存器状态.<br>
![alt text](./assets/ozone008.png)<br>   
 
## 4.3 Ozone连接出现连接丢失问题
经常连接一会就会出现如下Target Connection Lost的对话框，然后连接丢失<br>
![alt text](./assets/ozone009.png)<br>    
如果碰到以上问题，请更换Ozone的版本到Ozone_Windows_V320d_x64.zip版本，实测非常稳定。<br>
## 4.4 Ozone使能RTThread RTOS在线调试
复制\sdk\tools\segger\RtThreadOSPlugin.js文件到Ozone的安装目录:<br>
`C:\Program Files\SEGGER\Ozone\Plugins\OS\RtThreadOSPlugin.js`<br>
并且打开该文件，按照下面步骤操作，就可以使用Ozone在线切换RTThread线程进行查看和调试。<br>
![alt text](./assets/ozone010.png)<br>    
Ozone连接后，并使能Project.SetOSPlugin("RtThreadOSPlugin");的现场如下：<br>
 ![alt text](./assets/ozone011.png)<br>    
## 4.5 Ozone重定义文件路径
在烧录的bin的路径不是本地编译的情况下，用Ozone进行Debug，会提示File not find，无法定位到相应的c源代码，从而无法进行逐条跟踪定位问题。<br>
![alt text](./assets/ozone012.png)<br>     
解决方法：<br>
鼠标右键该文件，Locate File到对应文件，就能定位到该c源文件，也可以采用
Project.AddPathSubstitute命令重定位路径，实际是需要参考Qzone的手册<br>
