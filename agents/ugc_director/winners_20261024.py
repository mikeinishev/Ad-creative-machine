"""Authored production treatment for the eight requested source creatives.
Run with --source pointing at the original scripts.json and --out at a new pack.
"""
import argparse
import json
from pathlib import Path
from prepare import validate, render

# Each row is deliberately a different business situation, not a translated template.
ADS = {
'181': {
'angle':'Гости хвалят еду лично, но владелец в суете забывает попросить отзыв. Показать понятный момент для приглашения.',
'person':'middle-aged Chilean man, short dark beard and mustache, black forward baseball cap, plain black T-shirt, worn red apron',
'venue':'small Chilean sanguchería, stainless service counter, sandwiches wrapped in paper, ordinary pale walls, mixed window and fluorescent light',
'disclosure':'Recreación · demo del producto',
'lines':['Se van felices. ¿Y la reseña?', 'Mira: entre pedidos y cuentas, se me pasa pedirla. Así funciona Boomerang.', 'Pongo esta ruleta en la mesa. El cliente escanea y juega.', 'Después puede compartir su opinión en Google. Una opinión honesta.', 'Antes dependía de acordarme. Aquí, la invitación queda a mano.', 'Boomerang busca un restaurante. Revisa si el tuyo califica.'],
'visuals':['Owner finishes packing a sandwich, glances toward the departing guest, then at the phone lens. Immediate ordinary action; no long establishing shot.', 'Phone propped beside the till. Owner juggles a paper order and wipes the counter; then brings the small wheel table tent into frame. Show only one practical interruption.', 'Over the owner’s shoulder, he places the wheel table tent on a two-person table. One guest brings a phone to the code. Keep the same prop geometry.', 'Close side angle of guest holding phone after scanning. Screen stays angled and unreadable. Owner narrates; no generated review or star rating.', 'Owner returns the table tent to the same table next to a napkin holder; then resumes wrapping a sandwich. Match the earlier counter position.', 'Same owner at counter, relaxed direct address, table tent beside him. Small nod, no thumbs-up. Hold final composition after speech.'],
'ru':['Хук: довольный гость ушёл, отзыв остался неоставленным.', 'Узнаваемая суета и раннее знакомство с продуктом; разыгранная ситуация, не кейс.', 'Механика: поставить тейбл-тент, отсканировать QR, открыть игру.', 'Приглашение поделиться честным мнением, без обещания оценки.', 'Изменилось действие владельца, а не нарисованные цифры в Google.', 'Один ресторан и одно действие: проверить соответствие.'],
'overlays':['¿Y la reseña?', 'Entre pedidos y cuentas', 'Escanea · juega', 'Tu opinión cuenta', 'La invitación, a mano', '¿Tu restaurante califica?'],
'hooks':[('Se van felices. ¿Y la reseña?', 'Finish wrapping sandwich; look toward departing guest.', 'Entre pedidos y cuentas, se me pasa pedirla.'), ('El mejor comentario se quedó en esta mesa.', 'Owner clears an empty plate, then lifts the table tent.', 'Así les muestro cómo compartirlo.'), ('¿Pedir reseñas en plena hora punta?', 'An order lands beside the till as owner reaches for a table card.', 'Mira cómo lo pondría a mano.')]
},
'178': {
'angle':'Ареперия: просьба об отзыве теряется между кухней и кассой. Продукт как конкретный шаг при передаче счёта.',
'person':'middle-aged Colombian woman, short curly dark hair, small gold hoop earrings, yellow blouse, practical black apron',
'venue':'modest Colombian arepería, worn wood counter, tiled wall, a few plants, arepas on paper-lined plates, daylight and overhead practical lights',
'disclosure':'Recreación · demostración',
'lines':['La arepa sale. La reseña se queda pendiente.', 'Mira mi turno: cocina, caja, mesas. Pedir opiniones se me pasa. Te muestro Boomerang.', 'Dejo esta ruleta junto a la cuenta. El cliente escanea y juega.', 'Luego puede compartir lo que le pareció en Google, con sus propias palabras.', 'Así la invitación queda en la mesa, sin interrumpir otra vez.', 'Boomerang busca un restaurante. Mira si el tuyo aplica.'],
'visuals':['Owner slides a fresh arepa toward pickup and notices the empty table behind the counter.', 'Same fixed phone beside pickup; owner turns from order ticket to till and shows the table tent near the receipt.', 'Hands place receipt and table tent beside a finished arepa plate; guest scans the printed code.', 'Guest holds angled phone and considers response naturally; do not show generated text or reward for a review.', 'Wide phone shot of owner returning to service while the same card remains on table; ordinary occupancy.', 'Owner leans lightly on counter and speaks to lens. Keep arepa prep sounds low underneath.'],
'ru':['Хук через конкретный момент выдачи.', 'Показываем перегруз задачами и продукт.', 'Точка контакта — счёт.', 'Мнение гостя добровольное и своими словами.', 'После — приглашение остаётся на столе.', 'CTA для одного ресторана.'],
'overlays':['La reseña, pendiente', 'Cocina · caja · mesas', 'Junto a la cuenta', 'En sus propias palabras', 'Sin otra interrupción', 'Mira si aplica'],
'hooks':[('La arepa sale. La reseña se queda pendiente.', 'Slide arepa across pickup counter.', 'Entre cocina y caja se me pasa.'), ('¿Quién pide las reseñas cuando todos están ocupados?', 'Owner looks from till to pending paper orders.', 'Mira dónde dejaría la invitación.'), ('Esta cuenta puede abrir una conversación.', 'Set a receipt beside the wheel card.', 'Te muestro cómo funciona.')]
},
'167': {
'angle':'Американский cheesesteak shop: ещё один пассивный QR не объясняет, почему его сканировать. Показать повод начать взаимодействие.',
'person':'middle-aged American man, short beard, black backward baseball cap, plain black T-shirt, work-worn hands',
'venue':'ordinary Philadelphia cheesesteak shop, steel grill hood, stacked sandwich rolls, laminate tables and practical ceiling lights',
'disclosure':'Reenactment · product demo',
'lines':['Another QR code? Here’s the difference.', 'I’m showing Boomerang at my counter. Instead of just asking, I give guests something to try.', 'They scan this table card and open a little spin-the-wheel game.', 'Then they can share an honest Google review. The opinion is theirs.', 'The change is simple: a visible invitation, right where they already sit.', 'Boomerang is looking for one restaurant. See if yours qualifies.'],
'visuals':['Owner holds a plain unbranded QR card low, then sets wheel table tent beside it. No floating graphic comparison.', 'Owner at sandwich counter turns the wheel card toward camera while a sandwich is wrapped nearby.', 'Guest scans table tent; camera follows only enough to show phone interaction, screen unreadable.', 'Guest considering phone at table; relaxed, no exaggerated delight, no five-star closeup.', 'Return to table at same angle: wheel tent now next to napkin holder while guests eat normally.', 'Owner direct address beside steel counter, small matter-of-fact nod, final hold.'],
'ru':['Скептический вопрос от владельца.', 'Объясняем различие, показывая предмет.', 'Демонстрация первого шага.', 'Честное мнение остаётся выбором гостя.', 'До/после: пассивная просьба → заметное приглашение.', 'Один ресторан; проверка соответствия.'],
'overlays':['Another QR code?', 'Something to try', 'Scan · play', 'Their honest opinion', 'Right at the table', 'See if you qualify'],
'hooks':[('Another QR code? Here’s the difference.', 'Set a plain QR card beside the wheel card.', 'Give guests something to try.'), ('Would you scan this after lunch?', 'Hold wheel card beside a half-eaten cheesesteak.', 'Let me show you what opens.'), ('I don’t want my staff giving another sales pitch.', 'Owner frees hand from order pad and sets card on table.', 'Keep the invitation right here.')]
},
'188': {
'angle':'Турецкая pide: владелец скептически относится к ещё одному QR. Объяснить продукт на настоящем действии в зале.',
'person':'Turkish man in his forties, short curly hair, trimmed beard, plain white T-shirt and flour-dusted apron',
'venue':'small Turkish pide shop, brick oven, practical tiled wall, wooden service counter and plates of pide',
'disclosure':'Canlandırma · ürün demosu',
'lines':['Yine bir QR kod mu? Ben de öyle düşündüm.', 'Pide servisi arasında uzun uzun anlatamam. Boomerang’ın nasıl çalıştığını göstereyim.', 'Bu çarkı masaya koyuyorum. Müşteri kodu okutuyor, oyun açılıyor.', 'Sonra isterse Google’da kendi fikrini paylaşabiliyor. Yorum tamamen ona ait.', 'Fark şu: davet masada duruyor. Ben tekrar tekrar hatırlatmak zorunda kalmıyorum.', 'Boomerang bir restoran arıyor. Sizinki uygun mu, kontrol edin.'],
'visuals':['Owner sets down a flour-dusted peel and glances skeptically at wheel table tent next to counter.', 'He picks up tent and shows it while oven activity stays ordinary in background.', 'One hand places tent beside a pide plate; guest scans it with phone.', 'Guest with angled phone at table, no visible review text or rating; owner continues voiceover.', 'Owner returns to oven; tent remains in foreground at occupied table. Avoid implying customer growth.', 'Owner back at counter, speaks calmly into phone lens, no sales-person grin.'],
'ru':['Хук через недоверие к очередному QR.', 'Сервис важнее длинной презентации.', 'Показ действия.', 'Добровольное личное мнение.', 'После: меньше необходимости напоминать в демонстрации процесса.', 'Один ресторан и проверка.'],
'overlays':['Yine QR mı?', 'Nasıl çalışıyor?', 'Kodu okut · oyna', 'Kendi fikrin', 'Davet masada', 'Uygunluğunu kontrol et'],
'hooks':[('Yine bir QR kod mu? Ben de öyle düşündüm.', 'Skeptical glance at table tent beside oven peel.', 'Nasıl çalıştığını göstereyim.'), ('Pide soğumadan bunu göstereyim.', 'Set hot pide down next to wheel tent.', 'Müşteri kodu okutuyor.'), ('Her masaya aynı şeyi anlatmak mı?', 'Owner returns from table to oven.', 'Daveti masada bırakıyorum.')]
},
'190': {
'angle':'Рыбный ресторан: личная похвала не становится публичным мнением сама собой. Не обещать место в Maps или рост рейтинга.',
'person':'middle-aged Turkish man with curly short hair, trimmed facial hair, ordinary navy polo',
'venue':'neighborhood Turkish fish restaurant, simple window-side tables, plates of grilled fish, ordinary daylight, no cinematic sunset',
'disclosure':'Canlandırma · ürün demosu',
'lines':['“Balık harikaydı.” Peki, bunu kim duydu?', 'Güzel sözler masada kalabiliyor. Boomerang ile davetin nasıl değiştiğini göstereyim.', 'Masaya bu çarkı bırakıyorum. Müşteri telefonuyla kodu okutuyor ve oynuyor.', 'Ardından isterse deneyimini Google’da anlatabiliyor. Kendi cümleleriyle.', 'Önce sözlü bir rica. Sonra masada duran, kolayca görülen bir davet.', 'Boomerang bir restoran arıyor. Restoranınız uygun mu, bakın.'],
'visuals':['Owner clears an empty fish plate and repeats a common compliment to camera, not attributed to any real client.', 'At same table owner brings table tent into view and explains the demo.', 'Guest scans wheel tent beside fish plate; stable side angle and normal hand anatomy.', 'Phone held sideways to lens with unreadable screen; guest takes a moment, no theatrical reaction.', 'Match cut between empty place for tent and tent standing beside water glass; workflow comparison only.', 'Owner near service station, calm direct address; keep table tent visible behind shoulder.'],
'ru':['Личная похвала как узнаваемая ситуация.', 'Переход к демонстрации приглашения.', 'Сканирование и игра.', 'Рассказ гостя своими словами.', 'Сравнение процесса без выдуманных цифр.', 'Один ресторан.'],
'overlays':['Bunu kim duydu?', 'Masada kalmasın', 'Okut · oyna', 'Kendi cümleleriyle', 'Görünür bir davet', 'Uygun mu?'],
'hooks':[('“Balık harikaydı.” Peki, bunu kim duydu?', 'Clear an empty fish plate and turn to lens.', 'Güzel sözler masada kalabiliyor.'), ('Yorum istemek için doğru an ne zaman?', 'Bring receipt to a finished table.', 'Davet tam burada durabilir.'), ('Misafir memnun. Peki, davet nerede?', 'Show table without card then raise wheel tent.', 'Nasıl çalıştığını göstereyim.')]
},
'182': {
'angle':'Бразильский boteco: момент при оплате без неловкой длинной просьбы; приглашение на столе.',
'person':'older Brazilian man, short salt-and-pepper hair and beard, navy polo and practical white apron',
'venue':'ordinary Brazilian boteco, snack display, worn counter, simple yellow chairs, daylight, no alcohol in foreground',
'disclosure':'Encenação · demonstração do produto',
'lines':['Na hora da conta, eu lembro de tudo. Quase.', 'Pedir uma avaliação acaba ficando pra depois. Olha como funciona com a Boomerang.', 'Deixo essa roleta na mesa. A pessoa aponta o celular e joga.', 'Depois, se quiser, conta no Google como foi a experiência.', 'Antes era só um pedido falado. Agora a pessoa tem o convite ali.', 'A Boomerang procura um restaurante. Veja se o seu se qualifica.'],
'visuals':['Owner checks receipt and feels apron pocket for pen; glances at lens with a small knowing expression.', 'He shows wheel table tent next to receipt on worn counter, ordinary delivery.', 'Tent placed beside petiscos; guest scans with phone from sitting position.', 'Guest holds phone at table, unreadable screen, normal consideration not forced celebration.', 'Match same receipt/table angle before and after adding tent; owner returns to counter.', 'Owner at counter addresses lens casually, end on still composition with card visible.'],
'ru':['Небольшой бытовой недосмотр.', 'Проблема и продукт.', 'Простое действие гостя.', 'Добровольное мнение.', 'До/после действия, не бизнеса.', 'Один ресторан.'],
'overlays':['Quase tudo', 'Fica pra depois?', 'Apontou · jogou', 'Se quiser, conta', 'O convite fica ali', 'Veja se qualifica'],
'hooks':[('Na hora da conta, eu lembro de tudo. Quase.', 'Check receipt then pat apron pocket for pen.', 'A avaliação fica pra depois.'), ('Seu cliente elogia. E depois vai embora.', 'Clear empty snack plate, look toward doorway.', 'Olha onde fica o convite.'), ('Sem discurso na hora da conta.', 'Set card quietly beside receipt.', 'A pessoa vê como funciona.')]
},
'202': {
'angle':'Taquería: владелец умеет готовить, но не имеет плана привлечения. Продукт показывается как план, не история сотни уже пришедших гостей.',
'person':'Mexican man in his forties, black backward baseball cap, plain black T-shirt, practical apron',
'venue':'ordinary Mexican taquería, al pastor spit, stainless prep counter, modest tables before service',
'disclosure':'Recreación · demostración del plan',
'lines':['Tacos listos. ¿Cómo atraigo gente?', 'Antes de abrir, reviso todo menos la promoción. Así miraría mi zona con Richie.', 'Empiezo por mi restaurante y mi ubicación. No por publicar a ciegas.', 'La propuesta apunta a cien clientes nuevos en treinta días, según el plan.', 'Aquí reviso condiciones y presupuesto. Es una meta, no un resultado ya conseguido.', 'Buscan un solo restaurante por zona. Revisa si la tuya está disponible.'],
'visuals':['Owner places ready tacos on counter then gestures toward ordinary room before service; do not portray failure or sudden growth.', 'Phone propped by prep station. Owner checks paper prep list then opens phone for product demonstration; no fake metrics.', 'Over-shoulder phone interaction showing only unrecognizable neutral blocks; reserve real funnel capture for post insert.', 'Owner explains target at counter; simple post overlay labels it objective, never show graph or crowded-after montage.', 'Close view of hand using phone at counter, no readable fabricated price. Later insert verified offer terms if available.', 'Owner direct address with prep continuing quietly; keep occupancy identical throughout.'],
'ru':['Хук о недостающем плане.', 'До/после: подготовка кухни → проверка маркетингового плана.', 'Начать с ресторана и зоны.', '100 за 30 дней — предложение/цель, не результат кейса.', 'Условия и бюджет надо проверить.', 'Один ресторан на зону и проверка доступности.'],
'overlays':['¿Y el plan?', 'Richie · demo', 'Restaurante + zona', 'Objetivo: 100 / 30 días', 'Según plan y condiciones', 'Revisa tu zona'],
'hooks':[('Tacos listos. ¿Cómo atraigo gente?', 'Set tacos beside prep checklist.', 'Así miraría mi zona con Richie.'), ('Publicar otra foto no es mi plan completo.', 'Owner starts to photograph tacos, then lowers phone.', 'Primero miro mi restaurante y mi zona.'), ('Antes de gastar en anuncios, miro esto.', 'Phone beside unopened prep checklist.', 'Zona, plan y presupuesto.')]
},
'206': {
'angle':'Lokanta: у владельца мало времени на маркетинг. Показать переход от импровизации к проверке плана и условий.',
'person':'Turkish woman in her forties, loosely tied dark hair, small gold hoops, plain white top and practical black apron',
'venue':'ordinary Turkish lokanta, hot food service counter, modest tables, overhead lights, normal pre-service activity',
'disclosure':'Canlandırma · plan demosu',
'lines':['Yemeği ben yapıyorum. Tanıtımı da mı ben düşüneceğim?', 'Servisten önce her şeyi kontrol ediyorum. Tanıtım içinse net bir plan lazım. Richie’ye böyle bakıyorum.', 'Önce restoranımı ve bölgemi seçiyorum. Sonra bana uygun planı inceliyorum.', 'Hedef, plana göre otuz günde yüz yeni müşteri. Bu, gerçekleşmiş bir sonuç değil.', 'Bütçeyi ve koşulları kontrol ediyorum. Böylece neyi değerlendirdiğimi biliyorum.', 'Bölge başına tek bir restoran aranıyor. Bölgeniz açık mı, kontrol edin.'],
'visuals':['Owner closes a food tray lid, looks to phone camera with practical concern; no exaggerated distress.', 'Owner checks prep notebook at hot counter then uses phone; no chart or celebratory screen.', 'Over-shoulder phone interaction, screen angled and unreadable; real funnel capture can replace insert in post.', 'Direct-to-camera explanation of target with honest post overlay, no customer-arrival montage.', 'Phone and notebook together on counter as owner considers plan; no fabricated budget or price.', 'Owner near same food counter delivers one CTA with relaxed expression; final hold.'],
'ru':['Хук о двойной роли владельца.', 'Нужен план, показан продукт.', 'Ресторан → зона → план.', 'Цель с условиями, не обещание результата кейса.', 'Проверка бюджета и условий.', 'Один ресторан на зону.'],
'overlays':['Tanıtımı kim yapacak?', 'Richie · demo', 'Restoran + bölge', 'Hedef: 100 / 30 gün', 'Plan ve koşullara bağlı', 'Bölgeni kontrol et'],
'hooks':[('Yemeği ben yapıyorum. Tanıtımı da mı ben düşüneceğim?', 'Close food tray then glance at phone.', 'Net bir plan lazım.'), ('Servis hazır. Peki, tanıtım planı?', 'Check final item on prep notebook.', 'Önce bölgeme bakıyorum.'), ('Reklama başlamadan önce şunu kontrol ederim.', 'Phone beside work notebook.', 'Bölge, bütçe ve koşullar.')]
}
}

STYLE = ('Vertical 9:16 raw phone video, ordinary available mixed light, unretouched skin, '
         'normal dynamic range and slight handheld motion. A colleague records the owner at work. '
         'No cinematic grading, studio light, beauty filter, dramatic bokeh, slow motion, '
         'salesperson delivery, fake dashboard, readable invented phone UI, subtitles or graphic text. '
         'Do not depict sudden customer growth. Preserve venue, actor, clothes and table prop across shots. '
         'Natural room tone under clear speech, no music. Screens remain angled and unreadable. ')

def build(source):
    result = {'version':'ugc-director-1','date':'2026-10-24','status':'preproduction; renders and native-language QA pending','creatives':[]}
    for aid, data in ADS.items():
        original = source[aid]
        continuity = f"Same actor throughout: {data['person']}. Same venue: {data['venue']}."
        scenes=[]
        # Pair boundaries at 10, 20 and 30 seconds. Short hook and slower exposition.
        boundaries=[0,3,10,15,20,25,30]
        for i,line in enumerate(data['lines']):
            prompt = (f"{STYLE}{continuity}\nAction: {data['visuals'][i]}\n"
                      f"Audio: same owner's warm conversational {original['language']} voice, "
                      f"{'off-screen narration' if i in [2,3,4] else 'synchronized natural lip movement'}. "
                      f"Exact dialogue: {line}\nAllow natural breath; no added words. End with a short edit handle.")
            scenes.append({'id':f'{aid}_s{i+1:02d}','start':boundaries[i],'end':boundaries[i+1],
                'dialogue':line,'purpose_ru':data['ru'][i],'visual':data['visuals'][i],
                'overlay':data['overlays'][i], 'prompt':prompt,
                'frame_prompt':f"Photorealistic raw smartphone production storyboard still, vertical 9:16. {continuity} {data['visuals'][i]} Normal skin and light, no retouching or text overlay. Freeze the opening action of this scene. No fabricated readable phone UI.",
                'frame_status':'pending','transition':'ordinary hard cut; preserve ambient room tone'})
        clips=[]
        for i in range(3):
            selected=scenes[i*2:i*2+2]; offset=selected[0]['start']
            prompt=f"Exactly 10 seconds, vertical 9:16, two shots. {STYLE}{continuity}\n"
            for j,s in enumerate(selected):
                prompt+=f"\nSHOT {j+1} ({s['start']-offset}–{s['end']-offset}s): {s['visual']} Spoken only in {original['language']} by the same owner: \"{s['dialogue']}\". "
                prompt+= 'Owner voice-over, screen not legible.' if i==1 else 'Natural conversational delivery; lip sync when face is visible.'
            clips.append({'id':f'{aid}_c{i+1:02d}','duration':10,'scenes':[s['id'] for s in selected], 'prompt':prompt,'status':'not_generated'})
        ad={'source_id':aid,'product':original['funnel'],'language':original['language'],
            'duration':30,'reference_plate':original['plate'],'continuity':continuity,
            'hypothesis_ru':data['angle'],'disclosure':data['disclosure'],
            'hooks':[{'variant':chr(65+i),'spoken':h[0],'visual':h[1],'bridge':h[2]} for i,h in enumerate(data['hooks'])],
            'scenes':scenes,'clips':clips,
            'claim_ledger':[
                {'claim':'Owner situation and before/after','type':'fictional workflow demonstration','evidence':'User explicitly chose demonstration without customer cases','restriction':'Disclosure throughout. No actual-client results.'},
                {'claim':'Recruitment quantity','type':'offer instruction','evidence':'User: one restaurant, not five','restriction':'Do not imply a fabricated closing deadline.'},
                {'claim':'QR game / voluntary opinion' if original['funnel']=='getreviews' else '100 customers / 30 days',
                 'type':'product mechanism' if original['funnel']=='getreviews' else 'conditional target',
                 'evidence':'Original funnel analysis and source pack; verify live path before paid launch',
                 'restriction':'Do not condition a prize on posting a review or a positive rating; verify actual flow.' if original['funnel']=='getreviews' else 'Not an achieved result. Verify budget, eligibility and current terms before launch.'}],
            'edit_plan':{'master':'720x1280, 30s; retain native source quality',
                'assembly':'c01 → c02 → c03. Check face/voice/prop at both joins. Natural hard cuts. Match room tone; no loud music.',
                'captions':'Exact localized dialogue, short phrase chunks, max two lines, white with dark outline; do not overlap face, prop or platform controls.',
                'disclosure':data['disclosure']+' — readable throughout, not hidden in a single final frame.',
                'safe_area':'House working area x=80..640, y=190..820 at 720x1280 for essential overlays; verify actual Meta/TikTok preview.',
                'ui_insert':'Only genuine redacted capture with source URL/date. If unavailable, show action with unreadable screen; no screenshot claim.',
                'cutdown':'Separate 15–18s version needs rewritten dialogue; do not speed up 30s speech.',
                'audio':'Listen to every word, continuity and lip sync. Normalize consistently after assembly, avoid clipping; keep restaurant ambience.'},
            'qa':{'editorial':'pending independent second pass','visual':'not rendered','audio':'not rendered','native_speaker_review':'not yet performed','conversion':'untested'}}
        result['creatives'].append(ad)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    pack=build(json.loads(a.source.read_text()));errors=validate(pack)
    if errors: raise SystemExit('\n'.join(errors))
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'scripts.json').write_text(json.dumps(pack,ensure_ascii=False,indent=2))
    for ad in pack['creatives']:
        folder=a.out/'prompts'/ad['source_id'];folder.mkdir(parents=True,exist_ok=True)
        for clip in ad['clips']: (folder/(clip['id']+'.txt')).write_text(clip['prompt'])
        for scene in ad['scenes']: (folder/(scene['id']+'.txt')).write_text(scene['prompt'])
    render(pack,a.out)
    print(f'Authored {len(pack["creatives"])} creatives, 48 scenes, 24 clip prompts, 24 hooks; validation passed.')
