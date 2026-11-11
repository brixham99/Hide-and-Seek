"""Headless screenshots of Myrtle: on her bed, following in the Hall, sitting in the Kitchen (both cameras).

    python3 tools/myrtle_shots.py [out_dir]
"""
import os, sys, math
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),".."); sys.path.insert(0,ROOT); os.chdir(ROOT)
import pygame, game, house, dog
OUT=sys.argv[1] if len(sys.argv)>1 else "shots"; os.makedirs(OUT, exist_ok=True)
pygame.init(); screen=pygame.display.set_mode((1280,720))
g=game.Game(screen)
DT=1/30
def place(room,x,y,facing="N"):
    g.room,g.x,g.y,g.facing=room,x,y,facing; g.view=house.view_for(room,x); g.trans=None
def walk(room, pts, secs):
    place(room,*pts[0]); i=0
    for _ in range(int(secs/DT)):
        tx,ty=pts[(i+1)%len(pts)]; dx,dy=tx-g.x,ty-g.y; dd=math.hypot(dx,dy); s=3*DT
        if dd<=s: g.x,g.y=tx,ty; i+=1
        else: g.x+=dx/dd*s; g.y+=dy/dd*s
        g.facing=("E" if dx>0 else "W") if abs(dx)>=abs(dy) else ("S" if dy>0 else "N")
        if g.flipped: g.facing={"E":"W","W":"E","S":"N","N":"S"}[g.facing]
        g.moving=True; g.dist+=s
        g.dog.update(DT,g.room,g.x,g.y,True)
def idle(secs):
    g.moving=False
    for _ in range(int(secs/DT)): g.dog.update(DT,g.room,g.x,g.y,False)
def shot(name):
    for fl in (False,True):
        g.flipped=fl; g._hint=g._make_hint(); g.trans=None; g.draw()
        pygame.image.save(g.screen, f"{OUT}/myrtle_{name}_{'v' if fl else 'se'}.png")
    g.flipped=False
# 1 lying on bed
g.dog=dog.Dog(); place("drawing",4.6,3.9,"S"); g.moving=False; shot("bed")
print("bed", g.dog.state)
# 2 following in the hall: walk drawing -> hall
g.dog=dog.Dog()
walk("drawing",[(4.5,4.5),(5.6,5.4)],2)
walk("hall",[(1.6,0.9),(2.4,2.0),(2.4,1.0),(1.4,1.6)],9)
walk("hall",[(1.4,1.6),(2.3,2.6)],0.4)
print("hall", g.dog.room, g.dog.state, round(g.dog.x,2), round(g.dog.y,2), g.x, g.y)
shot("hall")
# 3 kitchen sit
walk("kd",[(9.0,1.0),(9.6,2.6),(9.6,1.4),(8.4,1.6)],2.8)
g.facing="N"; idle(4)
print("kitchen", g.dog.room, g.dog.state, round(g.dog.x,2), round(g.dog.y,2), round(g.x,2), round(g.y,2))
shot("kitchen")
