# medicine_inventory_system



## 前言

这是本人第一个项目写的不是很好



## 项目介绍

`medicine_inventory_system`本来是一个智能库存管理系统，是一个单体多模块项目，但是写着写着变样了。。。本项目包括前端操作页面(基于Vue3，Element-Plus编写)和后端管理系统（基于SpringBoot，MyBatis-Plus，Redis等）还有一个python编写的库存预测服务（这个代码非常简单，预测可能不正确）

后端地址：https://github.com/fish-8984/medicine_inventory_system

前端地址：https://github.com/fish-8984/medicine_inventory_system_vue

python预测服务地址：https://github.com/fish-8984/python_divinable

### 项目图片展示

![image](https://github.com/user-attachments/assets/83d775ca-a08d-4f14-a484-fc414c3989ed)




### 组织结构

```lua
medicine_inventory_system
├── common -- 工具类及通用代码
├── entity -- 实体类
├── notice -- 通知服务
├── repository -- 数据访问层
├── security -- SpringSecurity封装公用模块
├── service -- 业务逻辑层
└── web -- Web接口层
```



### 技术选型

#### 后端技术

| 技术           | 说明                | 官网                                           |
| -------------- | ------------------- | ---------------------------------------------- |
| SpringBoot     | Web应用开发框架     | https://spring.io/projects/spring-boot         |
| SpringSecurity | 认证和授权框架      | https://spring.io/projects/spring-security     |
| MyBatis-Plus   | ORM框架             | https://baomidou.com/introduce/                |
| Redis          | 内存数据存储        | https://redis.io/                              |
| Nginx          | 静态资源服务器      | https://www.nginx.com/                         |
| Docker         | 应用容器引擎        | https://www.docker.com                         |
| Druid          | 数据库连接池        | https://github.com/alibaba/druid               |
| JWT            | JWT登录支持         | https://github.com/jwtk/jjwt                   |
| Lombok         | Java语言增强库      | https://github.com/rzwitserloot/lombok         |
| PageHelper     | MyBatis物理分页插件 | http://git.oschina.net/free/Mybatis_PageHelper |



#### 前端技术

| 技术         | 说明             | 官网                                                         |
| ------------ | ---------------- | ------------------------------------------------------------ |
| Vue          | 前端框架         | https://vuejs.org/                                           |
| Vue-router   | 路由框架         | https://router.vuejs.org/                                    |
| Pinia        | 全局状态管理框架 | https://pinia.vuejs.org/                                     |
| Element-plus | 前端UI框架       | https://cn.element-plus.org/zh-CN/component/config-provider.html |
| Axios        | 前端HTTP框架     | https://github.com/axios/axios                               |



#### 结构图

![image](https://github.com/user-attachments/assets/3a42706a-36d4-4883-a4c4-417e1592c7ff)




## 环境搭建

### 开发工具

| 工具          | 说明                | 官网                                                  |
| ------------- | ------------------- | ----------------------------------------------------- |
| IDEA          | 开发IDE             | https://www.jetbrains.com/idea/download               |
| RedisDesktop  | redis客户端连接工具 | https://github.com/qishibo/AnotherRedisDesktopManager |
| Navicat       | 数据库连接工具      | http://www.formysql.com/xiazai.html                   |
| PowerDesigner | 数据库设计工具      | http://powerdesigner.de/                              |
| Axure         | 原型设计工具        | https://www.axure.com/                                |
| MindMaster    | 思维导图设计工具    | http://www.edrawsoft.cn/mindmaster                    |
| PicPick       | 图片处理工具        | https://picpick.app/zh/                               |
| Postman       | API接口调试工具     | https://www.postman.com/                              |
| Typora        | Markdown编辑器      | https://typora.io/                                    |



### 开发环境

| 工具   | 版本号 | 下载                                               |
| ------ | ------ | -------------------------------------------------- |
| JDK    | 17     | https://www.oracle.com/java/technologies/downloads |
| MySQL  | 8.0.40 | https://www.mysql.com/                             |
| Redis  | 5.0.14 | https://redis.io/download                          |
| Nginx  | 1.26.2 | http://nginx.org/en/download.html                  |
| Python | 3.9.22 | https://www.python.org/                            |







