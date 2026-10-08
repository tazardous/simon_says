"""Screenshots -> tests/shots/*.png"""
import os
from playwright.sync_api import sync_playwright
CH='/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
ROOT=__file__.rsplit('/tests/',1)[0]; URL='file://'+ROOT+'/index.html'; OUT=ROOT+'/tests/shots'; os.makedirs(OUT,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CH,args=['--no-sandbox']); pg=b.new_page(viewport={'width':430,'height':800})
    pg.add_init_script('window.__SSfast=true;'); pg.goto(URL); pg.wait_for_timeout(500)
    pg.screenshot(path=OUT+'/1_setup.png')
    pg.evaluate("__SS.newGame({players:3,level:1,avs:[0,3,5]});0"); pg.evaluate("__SS.G.players[0].pos=3;__SS.G.players[1].pos=3;__SS.G.players[2].pos=14;__SS.G.players[0].score=4;__SS.G.players[1].score=2;0")
    pg.evaluate("document.querySelector('#roll').click();0"); pg.wait_for_timeout(200); pg.screenshot(path=OUT+'/2_board.png')
    def card(t,lv,n):
        pg.evaluate(f"(()=>{{__SS.newGame({{players:2,level:{lv},avs:[0,1]}}); }})();0")
        pg.evaluate(f"document.querySelector('#modal').classList.remove('on');0")
        pg.evaluate(f"""(()=>{{ const orig=__SS.makeCard; }})();0""")
    for lv,t,n in [(0,'move','3_move_l1'),(1,'move','4_move_l2'),(0,'spell','5_spell_l1'),(1,'spell','6_spell_l2'),(2,'spell','7_spell_l3'),(1,'math','8_math_l2'),(0,'shape','9_shape_l1'),(2,'shape','10_shape_l3'),(2,'math','11_math_l3')]:
        pg.evaluate(f"__SS.newGame({{players:2,level:{lv},avs:[0,1]}});0")
        # open a card of the wanted type by forcing the die onto a matching space
        idx=pg.evaluate(f"__SS.SPACES.findIndex((s,i)=>i>0&&s.type==='{t}')")
        pg.evaluate(f"__SS.G.players[0].pos={idx-1};0"); pg.evaluate("__SS.roll(1);0"); pg.wait_for_timeout(900)
        pg.screenshot(path=f'{OUT}/{n}.png')
        pg.evaluate("document.querySelector('#modal').classList.remove('on');0")
    pg.evaluate("document.querySelector('#win').classList.add('on');document.querySelector('#winH').textContent='🦊 FOX WINS!';0"); pg.screenshot(path=OUT+'/12_win.png')
    b.close()
