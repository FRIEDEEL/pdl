# 4.2 嵌入图片

Image 在创建时捕获本地 PNG/JPEG 字节，并以毫米描述视口。contain 保留完整来源，cover 裁剪填满视口，stretch 改变纵横比。

仿射变换更新当前视口角点，保持像素数据。SVG 内嵌 data URL；保存 TikZ 时，将内容寻址的资源复制到源码旁，输出目录可以移动。此接口不处理 DPI、EXIF 朝向、像素解码、SVG/PDF 导入或透视图片变形。

## 可运行示例与输出

```{literalinclude} ../../../../examples/tutorial/media/images.py
:language: python
:start-after: "# tutorial-start"
:end-before: "# tutorial-end"
```

![19. 嵌入图片](../../../../examples/output/tutorial/media/images.svg)

完整源码：[images.py](../../../../examples/tutorial/media/images.py).

---

[本部分目录](index.md)
