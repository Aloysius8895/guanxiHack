"""Publish the supplied model with English controls and local dependencies."""
from pathlib import Path
from urllib.request import urlopen
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'

def main():
    vendor = SITE / '_assets/metrix/three'
    for name in ['build/three.module.js', 'build/three.core.js', 'examples/jsm/controls/OrbitControls.js', 'examples/jsm/geometries/RoundedBoxGeometry.js', 'examples/jsm/geometries/ExtrudeGeometry.js', 'examples/jsm/utils/BufferGeometryUtils.js']:
        dest = vendor / name
        if dest.exists():
            continue
        try:
            data = urlopen('https://unpkg.com/three@0.180.0/' + name, timeout=40).read()
        except Exception:
            if name.endswith('ExtrudeGeometry.js'):
                continue
            raise
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    html = (ROOT / 'MetriX-Rover-Six-Legs.html').read_text('utf-8')
    pairs = {
        'lang="zh"': 'lang="en"',
        'https://unpkg.com/three@0.180.0/': '/_assets/metrix/three/',
        'MetriX AI · Mine Crawler · Articulated Legs': 'MetriX Smart Sampling Rover',
        'MetriX AI · Mine Crawler': 'Smart Sampling Rover | MetriX AI',
        '参考图风格：左右各三组轮腿，前后斜向伸出，中间向侧面伸出。拖动旋转，滚轮缩放。': 'Six articulated wheel assemblies, a sampling arm and a sensor mast. Drag to rotate. Scroll to zoom.',
        '360° 展示': '360° Orbit', '行驶': 'Drive', '采样动作': 'Sample',
        '拆解视图': 'Exploded View', '重置视角': 'Reset View', '合上模型': 'Assemble',
        '采样机械臂与顶部传感器保留；前方突出探头已移除。': 'Hardware concept · Engineering and field validation pending.',
        '组成：圆形底盘 · 六轮 · 六组关节悬架 · 样品盘 · 传感器 · 采样机械臂': 'Chassis · Six wheels · Articulated suspension · Carousel · Sensors · Sampling arm',
        'MetriX 结构组成': 'Explore the Components',
        '圆形主底盘与护板': 'Circular chassis & armour',
        '六组关节悬架': 'Articulated suspension', '六组越野轮组': 'Six terrain wheels',
        '样品容器转盘': 'Sample carousel', 'LiDAR 与视觉传感器': 'LiDAR & vision sensors',
        '多关节采样臂': 'Articulated sampling arm',
        'const white=mat(0xbfc9d3,.52,.31)': 'const white=mat(0xf1f0ed,.25,.42)',
    }
    for old, new in pairs.items():
        html = html.replace(old, new)
    # Preserve the supplied geometry and interactions; use the reference's light shell.
    html = html.replace('const armor=mat(0x8a9aa7,.68,.36)', 'const armor=mat(0xe3e5e5,.3,.4)')
    # Match the reference's raised sensor mast while keeping its optics undistorted.
    html = html.replace('box(mast,.17,.48,.17,titanium,0,.33,0)', 'box(mast,.17,1.28,.17,titanium,0,.73,0)')
    html = html.replace('[.18,.39,.57]', '[.18,.79,1.17]')
    html = html.replace('[x,.57,-.04]', '[x,1.37,-.04]')
    for old, new in [('black,0,.68,0','black,0,1.48,0'),('steel,0,.79,0','steel,0,1.59,0'),('blue,0,.64,0','blue,0,1.44,0'),('black,0,.60,.20','black,0,1.40,.20'),('glass,x,.60,.34','glass,x,1.40,.34'),('Math.sin(a)*.303,.68,','Math.sin(a)*.303,1.48,')]:
        html = html.replace(old,new)
    html = html.replace('</style>', '\n#ui{max-width:350px}#ui a{color:#a8caff}canvas{touch-action:none}@media(max-width:600px){#ui{max-width:none}#hint{display:block;font-size:10px}}\n</style>')
    html = html.replace('<div class="row">', '<div class="row">', 1)
    # A readable fallback remains visible if the browser cannot create a WebGL context.
    html = html.replace('<script type="module">', '<noscript><p>Enable JavaScript to explore the interactive rover.</p><img src="/_assets/metrix/rover-reference.webp" alt="MetriX rover concept views" width="100%"></noscript><script type="module">', 1)
    dest = SITE / 'rover/index.html'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, 'utf-8')
    print('Published English rover with local Three.js dependencies.')

if __name__ == '__main__':
    main()
