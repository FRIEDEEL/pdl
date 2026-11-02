# 源码架构

Author 是唯一可编辑的绘图领域模型。Geometry 描述当前形状参数，Style 描述样式，
Entity 结合二者并提供数值位置查询。circle 等小写绘图工厂返回 Entity；纯几何从
`author.geometry` 导入，不要求共同 Geometry 基类。

## 职责与依赖

| 包 | 职责 | 边界 |
| --- | --- | --- |
| author.geometry | 点、路径、形状、显式坐标系、原生文字／TeX／图片描述及查询 | 数值仿射映射、工具、字体资源配置；不依赖 Entity、Canvas、renderer |
| author.style | 不可变样式、渐变、字体描述、资源策略 | 工具和资源发现；不管理几何归属 |
| author.transform.base / affine | 广义映射契约、有限仿射矩阵 | 数值数据和 Point／Vector 适配 |
| author.transform.operations | 即时几何转换及显式样式变化 | Geometry、Style；不依赖具体 Entity 类 |
| author.entity | 薄实体、绘图工厂、Group 归属、Gather 选择、定位、捕获 | geometry、style、transform、util；不导入 Canvas 或后端 |
| author.util | 公共基础设施和显式外部工具接口 | 标准库、第三方库、外部工具；不导入 pdl 领域对象 |
| canvas | 提交、图层、查询、视口和输出入口 | Author 和后端入口 |
| backends | SVG／TikZ 编码、最终 PDF 编译 | 当前 Author Entity 与 canvas.records.Page；不导入 Canvas 实现 |
| extensions.diagram / extensions.spatial | 参数化图示、3D、相机、可见性 | 核心 Author 和组件自身；不依赖输出适配器 |

3D 包使用标准拼写 `spatial`。几何可使用数值仿射类，transform.operations 则识别几何类型并
决定转换。数值映射和对象转换策略分开，没有运行时模块循环。util 返回普通测量数据、
原始字体轮廓命令或工具结果，不管理对象关系。根入口按需加载扩展，核心 2D 导入不加载图示／3D，
也不会通过导入 pdl_old 补齐实现。

## 当前几何与即时编辑

Entity 初始化直接持有传入几何；显式共享可变几何时，直接编辑会影响所有持有者。
Transform 计算目标当前结果并替换其几何，Circle 转成 Path 后 Entity 身份仍不变。
对象不保存待执行操作、累计矩阵或隐式局部坐标系。Entity.copy 隔离几何和成员，
解除复制根对象的父级及图层身份。

默认旋转／缩放围绕 Entity 参考点；center 和世界轴对齐包围盒锚点是不同查询。
显式应用矩阵使用其世界映射，around 指定支点。曲线目前要求仿射映射，非线性算法和近似策略仍待后续实现。
默认线宽不变；均匀 Rescale 可显式包含线宽，非均匀缩放不提供该选项。
渐变可把当前坐标写入样式数据，以随几何一起改变。

文字／TeX 保存基线位置、字号和当前朝向。普通 Text 在保持朝向手性的相似变换下保留原生表达；
TeX 仅在平移／旋转下保留原生表达。几何缩放将已测量的 TeX 转轮廓，避免改字号时固定尺寸不随之缩放。
文字的拉伸／剪切／镜像等也转路径，对该 Entity 不可逆。
不支持的复杂 SVG 轮廓转换会明确报错，包括视口 fit 要求缩放时。图片保存当前视口角点和源字节，
输出所需矩阵由当前数据推导。

## 归属和样式

Group 是 Entity，成员为单父级归属，坐标均为当前世界坐标。变换一起编辑现有成员，
后加入的成员不重放过去操作。成员 Style None 在加入和退出时均保持 None。
有效样式依次采用成员显式值、最近显式设置样式的祖先、成员自身默认值。
group.set_style 只改 Group；Gather 不建立归属，只对显式选中对象批量操作。
一次变换中重叠选择的 Group／成员只处理一次。

捕获保留成员的 None 样式，固定各对象自身默认值并复制 Group 归属。
因此仍可修改捕获 Group 的回退样式，移出成员后也会使用捕获时固定的自身默认值。

Layer 属于 Canvas，Group 占一个有效层，捕获后内部连续绘制；重排图层不改变几何。
Frame 是显式纯几何，frame_axes 创建可绘制 Group，其当前基向量和可视坐标轴一起变化。
普通对象不附带隐式 frame／space。

## 查询、捕获与输出时机

1. 创建并编辑 Author 对象。查询返回固定数值，不建立持续联动，也不决定覆盖顺序。
2. 需要尺寸或轮廓时调用字体／TeX 测量。RendererConfig／typography 统一查询和提交的资源策略。
3. Canvas.snapshot 捕获普通 Entity；add／draw 还记录顺序和图层身份。捕获副本固定有效样式、
   字体候选和排版。扩展展开成核心 Entity。
4. 视口策略确定页面和当前输出几何，后端通过 Page 契约编码 Entity 的 Geometry／Style。
   没有第二套 Resolved 场景层，也不把图示布局交给 TikZ。

原生 SVG 与 LaTeX 文字的栅格结果可能不同，原生 SVG 不嵌入字体文件。
TeX 缓存包含声明依赖和工具版本，未声明的环境变化需要显式失效处理。

## 验证与迁移

架构测试检查依赖方向、显式导入、核心导入范围和捕获后的单一 Entity 模型。
数值测试与渲染测试分开，集成测试实际编译 TeX、PDF、渐变、字体和可移动图片资源。

新测试验证新语义，文档和示例采用新 API。审查后移除工作区中的旧实现及旧测试，
完整开发历史仍保留在 Git 中。合并 dev 使用非快进合并，保留已审查的实现与文档提交历史。

[English](architecture.md)
