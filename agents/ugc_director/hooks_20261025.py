"""Author-approved visual hooks and two English product treatments."""
import copy
import json
from pathlib import Path

PRIMARY = Path('/Users/mikeinishev/Projects/Ad creatives machine=]')
OUT = PRIMARY / 'outputs/storyboards/2026.10.25_ugc_hooks_v3'
pack = json.loads((PRIMARY/'outputs/storyboards/2026.10.24_ugc_director_v2/scripts.json').read_text())
actions = {
 'chase': 'FRAME ONE: owner already hurrying toward the closing front door, holding a receipt. In the first two seconds the door closes before they reach it; owner stops and turns to colleague filming. Small believable comic frustration, no theatrical sprint.',
 'phone': 'FRAME ONE: phone filming the owner begins to tip sideways on the counter. Owner catches and steadies it within two seconds, face briefly close to lens, then steps back. One small natural wobble, not a spinning camera or a transition to another identity.',
 'plate': 'FRAME ONE: an empty plate starts slipping at the counter edge. Owner catches it immediately with both hands, pauses and looks straight at the colleague filming. Plate intact; one physically simple catch completed within two seconds.',
 'praise': 'FRAME ONE: owner turns sharply toward a departing guest who gives a friendly approving gesture. Owner immediately lifts their phone and looks between the phone and camera, puzzled. Phone screen angled away, no invented ratings. All action within two seconds.',
 'chair': 'FRAME ONE: owner sets a plate down in front of an obviously empty chair and addresses the chair as if it were a diner. After one second look up at colleague filming with a dry, straight-faced expression. Keep the empty chair visible from the first frame.',
 'under': 'FRAME ONE: owner in apron is crouching and peering under an empty restaurant table. Within two seconds their face emerges beside the empty chair and they look at colleague filming. Deadpan everyday comedy, no surreal effects.',
 'open': 'FRAME ONE: owner energetically swings the front door open with an inviting arm gesture; quick handheld pan reveals empty dining tables within two seconds. Natural pre-service light, no crowd materializing.'
}
changes = {
 '181': ('chase','¡Espere! ¿Y la reseña?','Se van felices, pero se me pasa pedirla. Mira cómo funciona Boomerang.'),
 '178': ('phone','Uy… un segundo.','Cocina, caja, mesas… ¿y acordarme de pedir opiniones? Mira cómo funciona Boomerang.'),
 '167': ('plate','Caught that. Forgot the review.','In the middle of a shift, asking slips my mind. Let me show you Boomerang.'),
 '188': ('chase','Bir dakika! Ya yorum?','Pide servisi arasında yorum istemeyi unutuyorum. Boomerang’ın nasıl çalıştığını göstereyim.'),
 '190': ('praise','Beğendiler. Peki, bunu kim duydu?','Güzel sözler masada kalabiliyor. Boomerang ile bu daveti nasıl yapabileceğimi göstereyim.'),
 '182': ('plate','O prato eu peguei. A avaliação, esqueci.','No meio da correria, pedir fica pra depois. Olha como funciona a Boomerang.'),
 '202': ('chair','¿Lo de siempre? Ah, no hay nadie.','Ya estoy hablando con las sillas. Para las horas tranquilas, necesito un plan. Mira Richie.'),
 '206': ('under','Müşterileri arıyorum. Burada da yoklar.','Şaka bir yana, sakin saatler için bir tanıtım planı lazım. Richie’ye böyle bakıyorum.')
}
english = [
 ('en_getreviews','getreviews','phone',[
  'Whoa. Give me a second.',
  'Running a restaurant is enough to remember. Asking for reviews slips through. Here’s Boomerang GetReviews.',
  'A guest scans this table card and opens a little wheel game.',
  'Then they can share an honest review on Google, if they want.',
  'The invitation stays on the table while I get back to service.',
  'Boomerang is looking for one restaurant. Check if yours qualifies.'
 ], 'Same owner throughout: woman in her forties, short wavy brown hair, plain olive T-shirt and worn charcoal apron, unretouched skin. Same venue: modest neighborhood cafe, wooden counter, simple two-person tables, coffee machine and natural window light. Neutral conversational English, no exaggerated regional accent.'),
 ('en_100plus','100plus','open',[
  'Doors open. Who knows we’re here?',
  'Great food still needs people to find it. Let me show you how I’d use Richie.',
  'I start with my restaurant and the area around it.',
  'The offer targets a hundred new customers in thirty days, depending on the plan.',
  'I check the budget and terms before deciding. No guessing what’s included.',
  'They’re looking for one restaurant per area. Check if yours is available.'
 ], 'Same owner throughout: man in his forties, short brown hair, light stubble, plain navy T-shirt and worn grey apron. Same venue: modest neighborhood grill with simple wooden tables, steel service counter and natural daylight. Neutral conversational English, no exaggerated regional accent.')
]
for aid,product,hook,dialogue,continuity in english:
 a=copy.deepcopy(pack['creatives'][0 if product=='getreviews' else 6]);a.update(source_id=aid,product=product,language='International English',continuity=continuity,reference_plate='',hypothesis_ru='Понятная ежедневная проблема владельца → видимое действие с продуктом → проверка доступности для одного ресторана.')
 for i,s in enumerate(a['scenes']):
  s['id']=f'{aid}_s{i+1:02}';s['dialogue']=dialogue[i];s['overlay']=dialogue[i]
 a['hooks']=[{'variant':v,'spoken':spoken,'visual':actions[h],'bridge':dialogue[1]} for v,spoken,h in [('A',dialogue[0],hook),('B','Another thing to remember during service?' if product=='getreviews' else 'Table for two. Anyone?', 'phone' if product=='getreviews' else 'chair'),('C','The compliment stayed at this table.' if product=='getreviews' else 'Looking for customers. Not under here.', 'praise' if product=='getreviews' else 'under')]]
 a['scenes'][1]['visual']='Owner steadies phone on counter, then addresses camera naturally while picking up the table card.' if product=='getreviews' else 'Owner walks back from the open doorway to the counter, picks up a phone and addresses the colleague filming.'
 for s in a['scenes']:
  s['visual']=s['visual'].replace('wrapping a sandwich','checking a paper order')
 changes[aid]=(hook,dialogue[0],dialogue[1]);pack['creatives'].append(a)

PRODUCT_LOCK=' Preserve the complete photographic LANDSCAPE table-tent insert in a clear upright acrylic holder with wide base. Preserve approved localized artwork: prize wheel LEFT; full headline, CTA and large QR RIGHT; realistic food photography. No wheel-only cards, generic icons, toy wheels, missing QR or simplified artwork. Match acrylic reflections, contact shadow and physical proportions.'
STYLE='Raw vertical 9:16 smartphone UGC, natural skin texture and available mixed light. No beauty filter, cinematic grading, studio light, slow motion, artificial bokeh, added titles or subtitles, readable invented phone UI, or music. Clear natural speech and quiet restaurant ambience. No fabricated customer outcomes. Keep actor, clothing, venue and props consistent. '
OUT.mkdir(parents=True,exist_ok=True)
for a in pack['creatives']:
 aid=a['source_id'];hook,line,bridge=changes[aid]
 a['visual_hook']=hook;a['disclosure']='Internal provenance only: generated product demonstration; no on-screen label.'
 a['scenes'][0].update(visual=actions[hook],dialogue=line,overlay=line,purpose_ru=f'Визуальный хук {hook}: действие с первого кадра, развязка до второй секунды.')
 a['scenes'][1]['dialogue']=bridge
 a['hooks'][0]={'variant':'A — selected','spoken':line,'visual':actions[hook],'bridge':bridge}
 for s in a['scenes']:
  s['frame_status']='needs revised production frame';s.pop('frame_asset',None);s.pop('frame_panel',None)
  s['prompt']=STYLE+a['continuity']+'\nAction: '+s['visual']+'\nExact dialogue in '+a['language']+': '+s['dialogue']+'\nSame warm conversational owner voice throughout. Natural lip sync when owner visible; voice-over for product shots.'
  s['frame_prompt']='Single vertical 9:16 photorealistic raw smartphone still. '+a['continuity']+' '+s['visual']+' Freeze the first moment of the action. No captions or overlay. No retouching. Phone screens angled away.'
 if a['product']=='getreviews':
  for scene in a['scenes']:
   scene['prompt']+=PRODUCT_LOCK
   scene['frame_prompt']+=PRODUCT_LOCK
 a['clips']=[]
 per_clip=2 if aid=='181' else 3
 duration=10 if aid=='181' else 15
 for i in range(6//per_clip):
  ss=a['scenes'][i*per_clip:i*per_clip+per_clip];start=ss[0]['start'];cid=f'{aid}_c{i+1:02}'
  prompt=f'Exactly {duration} seconds, 9:16. '+STYLE+a['continuity']+' Use attached image as identity and venue reference, not a static slide.\n'
  for j,s in enumerate(ss):prompt+=f'\nSHOT {j+1} ({s["start"]-start}–{s["end"]-start}s): {s["visual"]} Exact spoken {a["language"]}: "{s["dialogue"]}". Natural pace. '
  if a['product']=='getreviews':prompt+='\nPRODUCT LOCK:'+PRODUCT_LOCK
  a['clips'].append(dict(id=cid,duration=duration,scenes=[s['id'] for s in ss],prompt=prompt,status='not_generated'))
 a['edit_plan']['disclosure']='NONE. No recreation/demo label.'
 a['edit_plan']['assembly']=f'{len(a["clips"])} clips, natural hard cuts, inspect identity/voice/prop joins. No music; preserve natural speech and ambience.'
 for c in a['claim_ledger']:
  if c['claim']=='Owner situation and before/after':c['restriction']='Internal provenance only; no actual-client results and no on-screen demo labels.'
 a['qa']['visual']='Revised hook and English scenes require new production QA.'
 folder=OUT/'prompts'/aid;folder.mkdir(parents=True,exist_ok=True)
 for s in a['scenes']:(folder/(s['id']+'.txt')).write_text(s['prompt'])
 for c in a['clips']:(folder/(c['id']+'.txt')).write_text(c['prompt'])
pack['revision']='2026-10-25 approved visual hooks, no music or demo labels, two additional English videos'
(OUT/'scripts.json').write_text(json.dumps(pack,ensure_ascii=False,indent=2))
manifest={'status':'production_in_progress','videos':[{'source_id':a['source_id'],'hook':a['visual_hook'],'language':a['language'],'status':'script_ready','clips':a['clips']} for a in pack['creatives']]}
if not (OUT/'production.json').exists():
 (OUT/'production.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(OUT)
