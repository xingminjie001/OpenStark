from tornado.web import UIModule

#模块指向一个模板文件
class NavModule(UIModule):
    def render(self, total_page, page, limit, nav_url):
        return self.render_string('common/modules/nav.html', total_page=total_page, page=page, limit=limit, nav_url=nav_url)
