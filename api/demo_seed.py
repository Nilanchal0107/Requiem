"""Demo account for the pitch: login sunita / sunita123 with four saved reports (docs: Requiem pitch brief).

Numbers still come from the engine at seed time (ADR 0001). Only the explanation text is hardcoded, in EN/HI/MR,
with `{{figure_id}}` placeholders, so demo reports never call an LLM and pass the same verifier as live ones.
"""
from datetime import date, timedelta

from sqlmodel import Session, select

from api import db
from api.auth import hash_password
from api.contracts import EngineResult, Explanation, IntakeInput, Language, StageEvent
from data.loaders import load_archetypes, load_schemes
from engine import run_engine
from llm.verifier import verify

USERNAME, PASSWORD = "sunita", "sunita123"

_ELIGIBILITY = {
    "age": 34, "gender": "female", "social_category": "obc", "education": "10th_pass", "business_status": "new",
    "prior_subsidy": False, "prior_tarun_repaid": False, "artisan_trade": False, "farmland": "none",
}

# id, village code, archetype, unit scale, Own Contribution, text kind, days ago (oldest first in history)
REPORTS = [
    ("demo-onion-pimpalgaon", "563455", "onion_cultivation", 2, 100_000, "onion", 6),
    ("demo-dairy-25k-pimpalgaon", "563455", "dairy", 5, 25_000, "dairy_mudra", 4),
    ("demo-dairy-lasalgaon", "563424", "dairy", 5, 100_000, "dairy_pmegp", 2),
    ("demo-dairy-pimpalgaon", "563455", "dairy", 5, 100_000, "dairy_pmegp", 0),
]
_KIND = {r[0]: r[5] for r in REPORTS}

_SECTIONS = ("verdict", "market", "pricing", "risks", "path_to_yes", "next_steps")

# [kind][lang] = (six (title, text) pairs in _SECTIONS order, SWOT strengths/weaknesses/opportunities/threats)
TEXTS: dict[str, dict[str, tuple[list[tuple[str, str]], list[list[str]]]]] = {
    "dairy_pmegp": {
        "en": (
            [
                ("Good to start", "Your dairy can work. Your profit covers the loan repayment {{min_dscr}} times even in the hardest year, and you get your money back in about {{payback_months}} months."),
                ("Your village market", "Your village has about {{households}} homes, and milk is bought every day in almost all of them. Your five buffaloes give about {{our_capacity}} litres of milk a month. The milk cooperative buys all of it, so you do not need to find customers one by one."),
                ("Price and selling", "Sell to the village milk cooperative. It pays by fat content every ten days, so better feed means a better price. Keep a small part for direct sale to nearby homes and tea stalls, which usually pay more."),
                ("Risks to watch", "Animal illness is the biggest risk, so insure every buffalo and keep the vet's number ready. Milk drops in summer, and green fodder costs more then. Your Working capital of {{working_capital}} is there to cover feed until the milk money starts."),
                ("Can it be better?", "It already passes every check. Under PMEGP you get a subsidy of {{subsidy}}, which the bank adjusts against your Loan of {{loan}} after the lock-in period."),
                ("Next steps", "Apply for PMEGP online through the KVIC portal. Take your Aadhaar, bank passbook, caste certificate and this Bank DPR to the bank. Attend the short EDP training PMEGP asks for. Book the buffaloes only after the loan is sanctioned."),
            ],
            [
                ["Profit covers the EMI {{min_dscr}} times", "Cooperative buys all the milk"],
                ["Feed costs rise in summer", "Needs daily work, no holidays"],
                ["PMEGP subsidy of {{subsidy}}", "Sell ghee or curd later for more profit"],
                ["Animal illness or death", "Cooperative price can fall"],
            ],
        ),
        "hi": (
            [
                ("शुरू करना ठीक है", "आपकी डेयरी चल सकती है। सबसे कठिन साल में भी आपका मुनाफ़ा कर्ज़ की किस्त को {{min_dscr}} गुना ढक लेता है, और लगभग {{payback_months}} महीनों में आपका पैसा वापस आ जाता है।"),
                ("आपके गाँव का बाज़ार", "आपके गाँव में लगभग {{households}} घर हैं, और लगभग हर घर में रोज़ दूध खरीदा जाता है। आपकी पाँच भैंसें महीने में लगभग {{our_capacity}} लीटर दूध देंगी। दूध सहकारी संस्था सारा दूध खरीदती है, इसलिए आपको एक-एक ग्राहक नहीं ढूँढना पड़ेगा।"),
                ("दाम और बिक्री", "गाँव की दूध सहकारी संस्था को बेचें। वह फ़ैट के हिसाब से हर दस दिन में पैसा देती है, इसलिए अच्छा चारा मतलब अच्छा दाम। थोड़ा दूध पास के घरों और चाय की दुकानों को सीधे बेचें, वहाँ अक्सर ज़्यादा दाम मिलता है।"),
                ("ध्यान रखने वाले जोखिम", "पशु की बीमारी सबसे बड़ा जोखिम है, इसलिए हर भैंस का बीमा कराएँ और पशु डॉक्टर का नंबर पास रखें। गर्मी में दूध कम होता है और हरा चारा महँगा होता है। आपकी {{working_capital}} की कार्यशील पूँजी दूध का पैसा आने तक चारे का खर्च संभालेगी।"),
                ("क्या इसे और बेहतर किया जा सकता है?", "यह पहले से हर जाँच में पास है। PMEGP में आपको {{subsidy}} की सब्सिडी मिलती है, जिसे बैंक तय अवधि के बाद आपके {{loan}} के कर्ज़ में से घटा देता है।"),
                ("अगले कदम", "KVIC पोर्टल पर PMEGP के लिए ऑनलाइन आवेदन करें। आधार, बैंक पासबुक, जाति प्रमाणपत्र और यह बैंक DPR लेकर बैंक जाएँ। PMEGP की छोटी EDP ट्रेनिंग पूरी करें। कर्ज़ मंज़ूर होने के बाद ही भैंसें खरीदें।"),
            ],
            [
                ["मुनाफ़ा किस्त को {{min_dscr}} गुना ढकता है", "सहकारी संस्था सारा दूध खरीदती है"],
                ["गर्मी में चारे का खर्च बढ़ता है", "रोज़ काम, कोई छुट्टी नहीं"],
                ["PMEGP सब्सिडी {{subsidy}}", "आगे घी या दही बेचकर ज़्यादा मुनाफ़ा"],
                ["पशु की बीमारी या मौत", "सहकारी दाम गिर सकता है"],
            ],
        ),
        "mr": (
            [
                ("सुरू करायला हरकत नाही", "तुमची डेअरी चालू शकते. सर्वात कठीण वर्षातही तुमचा नफा कर्जाचा हप्ता {{min_dscr}} पट भरून काढतो, आणि साधारण {{payback_months}} महिन्यांत तुमचे पैसे परत येतात."),
                ("तुमच्या गावाचा बाजार", "तुमच्या गावात साधारण {{households}} घरे आहेत, आणि जवळजवळ प्रत्येक घरात रोज दूध घेतले जाते. तुमच्या पाच म्हशी महिन्याला साधारण {{our_capacity}} लिटर दूध देतील. दूध सहकारी संस्था सगळे दूध विकत घेते, म्हणून तुम्हाला एक-एक ग्राहक शोधावा लागणार नाही."),
                ("भाव आणि विक्री", "गावातील दूध सहकारी संस्थेला दूध विका. ती फॅटनुसार दर दहा दिवसांनी पैसे देते, म्हणून चांगला चारा म्हणजे चांगला भाव. थोडे दूध जवळच्या घरांना आणि चहाच्या टपऱ्यांना थेट विका, तिथे बऱ्याचदा जास्त भाव मिळतो."),
                ("लक्ष ठेवायचे धोके", "जनावरांचा आजार हा सर्वात मोठा धोका आहे, म्हणून प्रत्येक म्हशीचा विमा काढा आणि पशुवैद्यांचा नंबर जवळ ठेवा. उन्हाळ्यात दूध कमी होते आणि हिरवा चारा महाग होतो. तुमचे {{working_capital}} खेळते भांडवल दुधाचे पैसे येईपर्यंत चाऱ्याचा खर्च भागवेल."),
                ("अजून चांगले करता येईल का?", "हे आधीच प्रत्येक तपासणीत पास आहे. PMEGP मध्ये तुम्हाला {{subsidy}} अनुदान मिळते, जे बँक ठराविक काळानंतर तुमच्या {{loan}} कर्जातून वजा करते."),
                ("पुढची पावले", "KVIC पोर्टलवर PMEGP साठी ऑनलाइन अर्ज करा. आधार, बँक पासबुक, जातीचा दाखला आणि हा बँक DPR घेऊन बँकेत जा. PMEGP चे छोटे EDP प्रशिक्षण पूर्ण करा. कर्ज मंजूर झाल्यावरच म्हशी खरेदी करा."),
            ],
            [
                ["नफा हप्ता {{min_dscr}} पट भरून काढतो", "सहकारी संस्था सगळे दूध घेते"],
                ["उन्हाळ्यात चाऱ्याचा खर्च वाढतो", "रोजचे काम, सुट्टी नाही"],
                ["PMEGP अनुदान {{subsidy}}", "पुढे तूप किंवा दही विकून जास्त नफा"],
                ["जनावराचा आजार किंवा मृत्यू", "सहकारी भाव कमी होऊ शकतो"],
            ],
        ),
    },
    "dairy_mudra": {
        "en": (
            [
                ("Good to start, but costlier", "Your dairy can still work. Your profit covers the loan repayment {{min_dscr}} times in the hardest year, and you get your money back in about {{payback_months}} months."),
                ("Your village market", "Your village has about {{households}} homes, and your five buffaloes give about {{our_capacity}} litres of milk a month. The milk cooperative buys all of it, so selling is not the problem."),
                ("Price and selling", "Sell to the village milk cooperative, which pays by fat content every ten days. Sell a small part directly to nearby homes for a better price."),
                ("Risks to watch", "With only {{own_contribution}} of your own, you must borrow {{loan}}, and there is no subsidy. A sick animal or a dry summer will hurt more because the monthly repayment is bigger."),
                ("How to make it better", "If you can add more of your own money, you qualify for PMEGP and get a subsidy that lowers what you repay. Try it with the Try changes button."),
                ("Next steps", "Apply for a MUDRA Kishore loan at your bank with Aadhaar, bank passbook and this Bank DPR. Insure every buffalo. If you can save more first, check PMEGP again."),
            ],
            [
                ["Profit covers the EMI {{min_dscr}} times", "Cooperative buys all the milk"],
                ["No subsidy on this loan", "Bigger loan of {{loan}}"],
                ["More savings unlock PMEGP", "Sell curd or ghee later"],
                ["Animal illness", "Higher repayment in a bad month"],
            ],
        ),
        "hi": (
            [
                ("शुरू कर सकते हैं, पर महँगा", "आपकी डेयरी फिर भी चल सकती है। सबसे कठिन साल में भी मुनाफ़ा किस्त को {{min_dscr}} गुना ढकता है, और लगभग {{payback_months}} महीनों में पैसा वापस आता है।"),
                ("आपके गाँव का बाज़ार", "आपके गाँव में लगभग {{households}} घर हैं, और आपकी पाँच भैंसें महीने में लगभग {{our_capacity}} लीटर दूध देंगी। सहकारी संस्था सारा दूध खरीदती है, इसलिए बेचना समस्या नहीं है।"),
                ("दाम और बिक्री", "गाँव की दूध सहकारी संस्था को बेचें, जो फ़ैट के हिसाब से हर दस दिन में पैसा देती है। थोड़ा दूध पास के घरों को सीधे बेचें, वहाँ अच्छा दाम मिलता है।"),
                ("ध्यान रखने वाले जोखिम", "अपने सिर्फ़ {{own_contribution}} होने से आपको {{loan}} का कर्ज़ लेना होगा, और कोई सब्सिडी नहीं है। बीमार पशु या सूखी गर्मी का असर ज़्यादा होगा, क्योंकि हर महीने की किस्त बड़ी है।"),
                ("इसे बेहतर कैसे करें", "अगर आप अपना थोड़ा और पैसा लगा सकें, तो आप PMEGP के लिए योग्य होंगी और सब्सिडी से कर्ज़ घटेगा। बदलाव आज़माएँ बटन से देखें।"),
                ("अगले कदम", "आधार, बैंक पासबुक और यह बैंक DPR लेकर बैंक में MUDRA किशोर कर्ज़ के लिए आवेदन करें। हर भैंस का बीमा कराएँ। पहले और बचत हो सके तो PMEGP फिर से देखें।"),
            ],
            [
                ["मुनाफ़ा किस्त को {{min_dscr}} गुना ढकता है", "सहकारी संस्था सारा दूध खरीदती है"],
                ["इस कर्ज़ पर सब्सिडी नहीं", "बड़ा कर्ज़ {{loan}}"],
                ["ज़्यादा बचत से PMEGP मिलेगा", "आगे दही या घी बेचें"],
                ["पशु की बीमारी", "खराब महीने में बड़ी किस्त"],
            ],
        ),
        "mr": (
            [
                ("सुरू करता येईल, पण महाग", "तुमची डेअरी तरीही चालू शकते. सर्वात कठीण वर्षातही नफा हप्ता {{min_dscr}} पट भरून काढतो, आणि साधारण {{payback_months}} महिन्यांत पैसे परत येतात."),
                ("तुमच्या गावाचा बाजार", "तुमच्या गावात साधारण {{households}} घरे आहेत, आणि तुमच्या पाच म्हशी महिन्याला साधारण {{our_capacity}} लिटर दूध देतील. सहकारी संस्था सगळे दूध घेते, म्हणून विक्रीची अडचण नाही."),
                ("भाव आणि विक्री", "गावातील दूध सहकारी संस्थेला विका, ती फॅटनुसार दर दहा दिवसांनी पैसे देते. थोडे दूध जवळच्या घरांना थेट विका, तिथे चांगला भाव मिळतो."),
                ("लक्ष ठेवायचे धोके", "तुमचे फक्त {{own_contribution}} असल्याने तुम्हाला {{loan}} कर्ज घ्यावे लागेल, आणि अनुदान नाही. आजारी जनावर किंवा कोरडा उन्हाळा जास्त त्रास देईल, कारण दर महिन्याचा हप्ता मोठा आहे."),
                ("हे चांगले कसे करायचे", "तुम्ही स्वतःचे थोडे अजून पैसे घालू शकलात, तर तुम्ही PMEGP साठी पात्र व्हाल आणि अनुदानाने कर्ज कमी होईल. बदल करून पहा बटण वापरा."),
                ("पुढची पावले", "आधार, बँक पासबुक आणि हा बँक DPR घेऊन बँकेत MUDRA किशोर कर्जासाठी अर्ज करा. प्रत्येक म्हशीचा विमा काढा. आधी अजून बचत करता आली तर PMEGP पुन्हा तपासा."),
            ],
            [
                ["नफा हप्ता {{min_dscr}} पट भरून काढतो", "सहकारी संस्था सगळे दूध घेते"],
                ["या कर्जावर अनुदान नाही", "मोठे कर्ज {{loan}}"],
                ["जास्त बचतीने PMEGP मिळेल", "पुढे दही किंवा तूप विका"],
                ["जनावराचा आजार", "वाईट महिन्यात मोठा हप्ता"],
            ],
        ),
    },
    "onion": {
        "en": (
            [
                ("Not feasible for you right now", "Onion farming is not a good fit for you today. The main reason is land: onion loans come through the Kisan Credit Card, and it needs farmland in your name, which you do not have."),
                ("Your village market", "Your village has about {{households}} homes, and Lasalgaon nearby is the biggest onion market in the country, so selling would be easy. Two acres would give about {{our_capacity}} quintals a month in season."),
                ("Price and selling", "Onion prices swing a lot from month to month. Farmers who store onions in a kanda chal and sell later usually get a much better price than at harvest."),
                ("Risks to watch", "Without a matching scheme, the Project Cost of {{project_cost}} would need a loan of {{loan}} with no subsidy, and no bank scheme fits that today. Prices and unseasonal rain are the other big risks."),
                ("What would change this", "Leasing or owning farmland in your name would open the Kisan Credit Card. Until then, dairy suits you much better with the same money."),
                ("Next steps", "Compare this with your dairy report, which is good to start. If your family has farmland, ask about putting it in your name, then check onion again."),
            ],
            [
                ["Lasalgaon onion market is nearby", "Payback in about {{payback_months}} months"],
                ["No farmland in your name", "No scheme matches today"],
                ["Kanda chal storage gets better prices", "Land lease could open KCC"],
                ["Prices swing a lot", "Unseasonal rain"],
            ],
        ),
        "hi": (
            [
                ("अभी आपके लिए संभव नहीं", "आज प्याज़ की खेती आपके लिए ठीक नहीं है। मुख्य कारण ज़मीन है: प्याज़ का कर्ज़ किसान क्रेडिट कार्ड से मिलता है, और उसके लिए आपके नाम पर खेत चाहिए, जो आपके पास नहीं है।"),
                ("आपके गाँव का बाज़ार", "आपके गाँव में लगभग {{households}} घर हैं, और पास में लासलगाँव देश की सबसे बड़ी प्याज़ मंडी है, इसलिए बेचना आसान होता। दो एकड़ से मौसम में महीने का लगभग {{our_capacity}} क्विंटल प्याज़ मिलता।"),
                ("दाम और बिक्री", "प्याज़ के दाम महीने-दर-महीने बहुत बदलते हैं। जो किसान कांदा चाल में प्याज़ रखकर बाद में बेचते हैं, उन्हें कटाई के समय से अक्सर बहुत अच्छा दाम मिलता है।"),
                ("ध्यान रखने वाले जोखिम", "मिलती-जुलती योजना न होने से {{project_cost}} की परियोजना लागत के लिए बिना सब्सिडी {{loan}} का कर्ज़ चाहिए, और आज कोई बैंक योजना इसमें फिट नहीं होती। दाम और बेमौसम बारिश दूसरे बड़े जोखिम हैं।"),
                ("क्या बदलने से यह बनेगा", "अपने नाम पर खेत पट्टे पर लेने या होने से किसान क्रेडिट कार्ड खुल जाएगा। तब तक, उसी पैसे में डेयरी आपके लिए कहीं बेहतर है।"),
                ("अगले कदम", "इसकी तुलना अपनी डेयरी रिपोर्ट से करें, जो शुरू करने लायक है। अगर परिवार के पास खेत है, तो उसे अपने नाम करने के बारे में पूछें, फिर प्याज़ दोबारा देखें।"),
            ],
            [
                ["पास में लासलगाँव प्याज़ मंडी", "लगभग {{payback_months}} महीनों में पैसा वापस"],
                ["आपके नाम पर खेत नहीं", "आज कोई योजना फिट नहीं"],
                ["कांदा चाल से अच्छा दाम", "पट्टे की ज़मीन से KCC खुल सकता है"],
                ["दाम बहुत बदलते हैं", "बेमौसम बारिश"],
            ],
        ),
        "mr": (
            [
                ("सध्या तुमच्यासाठी शक्य नाही", "आज कांदा शेती तुमच्यासाठी योग्य नाही. मुख्य कारण जमीन आहे: कांद्याचे कर्ज किसान क्रेडिट कार्डमधून मिळते, आणि त्यासाठी तुमच्या नावावर शेतजमीन लागते, जी तुमच्याकडे नाही."),
                ("तुमच्या गावाचा बाजार", "तुमच्या गावात साधारण {{households}} घरे आहेत, आणि जवळच लासलगाव ही देशातील सर्वात मोठी कांदा बाजारपेठ आहे, म्हणून विक्री सोपी झाली असती. दोन एकरातून हंगामात महिन्याला साधारण {{our_capacity}} क्विंटल कांदा मिळाला असता."),
                ("भाव आणि विक्री", "कांद्याचे भाव महिन्या-महिन्याला खूप बदलतात. जे शेतकरी कांदा चाळीत कांदा साठवून नंतर विकतात, त्यांना काढणीच्या वेळेपेक्षा बऱ्याचदा खूप चांगला भाव मिळतो."),
                ("लक्ष ठेवायचे धोके", "जुळणारी योजना नसल्याने {{project_cost}} प्रकल्प खर्चासाठी अनुदानाशिवाय {{loan}} कर्ज लागेल, आणि आज कोणतीही बँक योजना यात बसत नाही. भाव आणि अवकाळी पाऊस हे इतर मोठे धोके आहेत."),
                ("काय बदलले तर हे जमेल", "तुमच्या नावावर शेतजमीन भाड्याने घेतली किंवा असली तर किसान क्रेडिट कार्ड मिळेल. तोपर्यंत, त्याच पैशात डेअरी तुमच्यासाठी खूप चांगली आहे."),
                ("पुढची पावले", "याची तुलना तुमच्या डेअरी अहवालाशी करा, जो सुरू करण्यासारखा आहे. कुटुंबाकडे शेतजमीन असेल तर ती तुमच्या नावावर करण्याबद्दल विचारा, मग कांदा पुन्हा तपासा."),
            ],
            [
                ["जवळच लासलगाव कांदा बाजार", "साधारण {{payback_months}} महिन्यांत पैसे परत"],
                ["तुमच्या नावावर जमीन नाही", "आज कोणतीही योजना जुळत नाही"],
                ["कांदा चाळीमुळे चांगला भाव", "भाड्याच्या जमिनीने KCC मिळू शकते"],
                ["भाव खूप बदलतात", "अवकाळी पाऊस"],
            ],
        ),
    },
}


def is_demo(report_id: str) -> bool:
    return report_id in _KIND


def demo_explanation(report_id: str, language: Language, figures: dict) -> Explanation:
    """The hardcoded explanation for a demo report, counted by the same verifier as a live one."""
    sections, swot = TEXTS[_KIND[report_id]][language]
    texts = [text for _, text in sections] + [item for group in swot for item in group]
    results = [verify(t, figures) for t in texts]
    offending = [s for r in results for s in r.offending]
    assert not offending, f"demo text breaks the verifier: {offending}"
    verified = sum(r.verified for r in results)
    return Explanation.model_validate({
        "language": language,
        "sections": [{"key": k, "title": title, "text": text} for k, (title, text) in zip(_SECTIONS, sections)],
        "swot": dict(zip(("strengths", "weaknesses", "opportunities", "threats"), swot)),
        "verified": verified,
        "total": verified,
        "regenerated": False,
        "available": True,
    })


def _stages(villages_verified_on: str) -> list[dict]:
    """The same stage trail a live build leaves, so the stream replay looks like a real run."""
    trail = [
        ("intake", ["User-entered"], 12), ("market", ["Census 2011", "OpenStreetMap", "archetypes.json (assumptions)"], 48),
        ("cost", ["archetypes.json (assumptions)"], None), ("schemes", [f"schemes.json (verified {villages_verified_on})"], None),
        ("dpr", ["Calculation engine"], None), ("explanation", ["LLM explanation"], 4200),
    ]
    return [StageEvent(stage=s, status="done", duration_ms=ms, sources=src).model_dump(mode="json") for s, src, ms in trail]


def seed_demo(session: Session) -> None:
    """Creates the demo Entrepreneur and the four reports once; a no-op when the account already exists."""
    if session.exec(select(db.User).where(db.User.username == USERNAME)).first():
        return
    user = db.User(username=USERNAME, password_hash=hash_password(PASSWORD))
    session.add(user)
    session.flush()

    archetypes = {a.id: a.model_dump(mode="json") for a in load_archetypes()}
    schemes = load_schemes()
    scheme_dicts = [s.model_dump(mode="json") for s in schemes]
    verified_on = str(min(s.verified_on for s in schemes))
    for report_id, village_code, archetype_id, scale, own, _, days_ago in REPORTS:
        village = session.get(db.Village, village_code)
        assert village is not None, f"seed_villages must run first: {village_code} missing"
        intake = IntakeInput(
            village_code=village_code, archetype_id=archetype_id, unit_scale=scale,
            own_contribution=own, eligibility=_ELIGIBILITY, language="en",
        )
        result: EngineResult = run_engine(
            intake, archetypes[archetype_id], scheme_dicts, village.model_dump(), current_year=date.today().year
        )
        session.add(db.Report(
            id=report_id,
            owner_id=user.id,
            status="done",
            input=intake.model_dump(mode="json"),
            engine=result.model_dump(mode="json"),
            explanation=demo_explanation(report_id, "en", result.figures).model_dump(mode="json"),
            stages=_stages(verified_on),
            created_at=db.utcnow() - timedelta(days=days_ago),
        ))
    session.commit()
