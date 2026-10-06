// Chinese pages only (/zh/): main.js derives the page-transition label from each page's Barba
// namespace ("About Us", "Services", ...); give it the Chinese page name instead.
window.metrixPageLabel = function (label) {
  return {
    'Home': '首页',
    'About Us': '关于 MetriX',
    'Technology': '技术',
    'Services': 'AI 解决方案',
    'Safety': '人工复核',
    'Privacy': '数据与产品范围',
    'Blog': '洞察',
    'Article': '文章'
  }[label] || label;
};
