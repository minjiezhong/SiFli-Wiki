# 10 系统
## 10.1 Lcpu中ROM空间中固化的函数和变量该如何调用和替换?
  为了节省Lcpu RAM空间的代码，ROM中固化了BLE协议栈，RTT OS，完整的HAL代码和部分驱动代码，<br> 
Lcpu中，可以供客户调用的函数和变量，都通过symble file的方式放在:<br> 
`SDK\example\ble\lcpu_general\project\ec-lb551\rom.sym `文件中，并且声明为不带__weak参数的强函数.<br> 

因此编写代码时，在能调用ROM代码的情况， 都会尽量调用ROM中代码.
比如:<br> 
你在SDK中看到文件bf0_hal_i2c.c中函数HAL_I2C_Mem_Read，会参加编译，但是在链接时，该处定义成了弱函数:<br> 
```c
#define __HAL_ROM_USED __weak 
``` 
<br>![alt text](./assets/system/system001.png)<br>  
而在对应的example\ble\lcpu_general\project\ec-lb551\rom.sym 文件中，如下图:<br> 
<br>![alt text](./assets/system/system002.png)<br>  

也有同名函数，并且不是__weak弱函数， 因此会链接到ROM的强函数代码去，因此上面的rt_kprintf并不会打印出来.<br> 
如果想跑该HAL_I2C_Mem_Read的函数，替换掉ROM中的函数，先删除example\ble\lcpu_general\project\ec-lb551\rom.sym # 该路径项目不同会不一样，可以查看编译过程log来定位，如下图：<br> 
<br>![alt text](./assets/system/system003.png)<br>   
再命令scons -c清掉lcpu编译结果重新编译，文件中对应的0x00005621 T HAL_I2C_Mem_Read 这一行，编译链接时，由于只存在这一个HAL_I2C_Mem_Read弱函数， 就会链接这个 __weak函数<br> 
这时上图中，你添加的rt_kprintf("my own HAL_I2C_Mem_Read\r\n");打印， 就能打印出来.<br> 
确认用的是ROM内函数还是代码中函数，可以在Lcpu编译出来的map文件内搜索这个函数对应地址来确认。<br> 

## 10.2 获取当前重启方式接口
目前SF32LB55X芯片，可以辨别的启动状态如下:<br> 
```c
/** power on mode */
typedef enum
{
    PM_COLD_BOOT = 0，  /**< cold boot */
    PM_STANDBY_BOOT,   /**< boot from standby power mode */
    PM_HIBERNATE_BOOT, /**< boot from hibernate mode, system can be woken up by RTC and PIN precisely */
    PM_SHUTDOWN_BOOT   /**< boot from shutdown mode, system can be woken by RTC and PIN, but wakeup time is not accurate */
} pm_power_on_mode_t;
```
可以通过调用:<br> 
```c
pm_power_on_mode_t SystemPowerOnModeGet(void)
{
    return g_pwron_mode;
}
```
来获取启动的模式;<br> 
注意:  上电， wdt，按键reset和HAL_PMU_Reboot四种cold root是没法区分;<br> 
## 10.3 main函数是lcpu的入口函数吗
lcpu复位地址在<br> 
<br>![alt text](./assets/system/system004.png)<br>   
main函数， 是做完了初始化后， 起的其中一个线程的main函数;<br> 

## 10.4 Lcpu如何唤醒Hcpu
a，Lcpu可以通过 ipc_send_msg_from_sensor_to_app往hcpu发消息如下，此消息能唤醒Hcpu<br> 
```c
static void battery_send_event_to_app(event_type_t type)
{
    event_remind_t remind_ind;

    rt_kprintf("battery_send_event_to_app: event %d\n", type);
    remind_ind.event = type;
    ipc_send_msg_from_sensor_to_app(SENSOR_APP_EVENT_BATTERY_IND, sizeof(event_remind_t), &remind_ind);
}
```
b，Hcpu端醒来后，在task中，添加处理该消息的代码，如下：
<br>![alt text](./assets/system/system005.png)<br>  


