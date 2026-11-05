"""Privacy Policy and DPDP Act 2023 Compliance page."""

import textwrap
import streamlit as st
from ui.state import get_language


def render_privacy_page():
    """Render comprehensive DPDP Act 2023 compliant privacy policy."""
    lang = get_language()

    if lang == "mr":
        st.title("🛡️ गोपनीयता धोरण व शेतकरी डेटा हक्क (DPDP Act, 2023)")
        st.caption("डिजिटल वैयक्तिक डेटा संरक्षण कायदा, २०२३ अंतर्गत कृषी साथी AI चे अधिकृत धोरण")

        st.markdown(
            textwrap.dedent("""
            ### १. डेटा संकलनाचा उद्देश (Purpose of Collection)
            कृषी साथी AI (AgriSaathi AI) खालील शेतीविषयक उद्दिष्टांसाठीच आपला डेटा संकलित करते:
            - **अचूक पीक सल्ला**: हवामान, मातीचा प्रकार व पिकांच्या स्थितीनुसार मार्गदर्शन करणे.
            - **स्थानिक बाजारभाव**: जवळच्या कृषी उत्पन्न बाजार समित्यांमधील (APMC Mandis) थेट व विश्लेषित दर दाखवणे.
            - **शेती व्यवस्थापन**: शेतातील दैनंदिन कामे, खर्च आणि उत्पादनाची डिजिटल नोंद ठेवणे.

            ### २. डेटा फिड्युशियरी (Data Fiduciary Responsibility)
            - **प्लॅटफॉर्म**: AgriSaathi AI (कृषी साथी AI)
            - **डेटा सुरक्षा**: आपले सर्व पासवर्ड **Argon2id** क्रिप्टोग्राफिक हॅश अल्गोरिदमने सुरक्षित आहेत.
            - **शून्य-विक्री हमी (Zero-Sale Guarantee)**: शेतकऱ्यांचा कोणताही वैयक्तिक डेटा कोणत्याही जाहिरातदार किंवा तृतीय पक्षाला विकला किंवा भाड्याने दिला जात नाही.

            ### ३. शेतकऱ्यांचे कायदेशीर हक्क (Data Principal Rights)
            DPDP कायदा २०२३ नुसार प्रत्येक नोंदणीकृत शेतकऱ्याला खालील अधिकार प्राप्त आहेत:
            1. **माहिती मिळवण्याचा हक्क (Right to Access)**: आपल्या प्रोफाइलमध्ये साठवलेली सर्व माहिती पाहणे.
            2. **डेटा डाउनलोड करण्याचा हक्क (Right to Data Portability / Export)**: आपल्या प्रोफाइल सेटिंग्जमधून संपूर्ण शेती नोंदी एका क्लिकवर **JSON स्वरूपात डाउनलोड** करणे.
            3. **दुरुस्तीचा हक्क (Right to Correction)**: प्रोफाइलमधील कोणतीही चुकीची माहिती अद्ययावत करणे.
            4. **खाते नष्ट करण्याचा हक्क (Right to Erasure / Deletion)**: कोणत्याही वेळी आपले खाते आणि सर्व शेती नोंदी **कायमस्वरूपी नष्ट (Delete)** करणे.

            ### ४. तक्रार निवारण (Grievance Redressal)
            काही शंका अथवा तक्रार असल्यास शेतकऱ्यांनी खालील अधिकृत संपर्क माध्यमांवर संपर्क साधावा:
            - **अधिकृत ईमेल**: privacy@agrisaathi.com
            - **किसान कॉल सेंटर (तातडीच्या सल्ल्यासाठी)**: **1800-180-1551** (टोल-फ्री)
            """).strip()
        )
    elif lang == "hi":
        st.title("🛡️ गोपनीयता नीति एवं किसान डेटा अधिकार (DPDP Act, 2023)")
        st.caption("डिजिटल व्यक्तिगत डेटा संरक्षण अधिनियम, 2023 के अंतर्गत आधिकारिक नीति")

        st.markdown(
            textwrap.dedent("""
            ### 1. डेटा संग्रह का उद्देश्य (Purpose of Collection)
            कृषि साथी AI केवल निम्नलिखित कृषि उद्देश्यों के लिए डेटा एकत्र करता है:
            - **सटीक फसल सलाह**: मौसम, मिट्टी एवं फसल स्थिति के अनुसार मार्गदर्शन।
            - **स्थानीय मंडी भाव**: निकटतम मंडियों (APMC) के ताजा व विश्लेषित भाव।
            - **फार्म प्रबंधन**: फसल कार्य, खर्च एवं उत्पादन का डिजिटल रिकॉर्ड।

            ### 2. डेटा सुरक्षा गारंटी
            - सभी पासवर्ड **Argon2id** क्रिप्टोग्राफिक हैशिंग द्वारा सुरक्षित हैं।
            - किसानों का व्यक्तिगत डेटा कभी भी किसी तीसरे पक्ष या विज्ञापनदाता को नहीं बेचा जाता।

            ### 3. किसान के कानूनी अधिकार (Data Principal Rights)
            - **डेटा देखने का अधिकार**: अपनी संपूर्ण जानकारी देखने का अधिकार।
            - **डेटा डाउनलोड (Export) का अधिकार**: अपनी प्रोफाइल से एक क्लिक में **JSON डेटा डाउनलोड** करें।
            - **डेटा संशोधन का अधिकार**: किसी भी जानकारी को अपडेट करने का अधिकार।
            - **खाता एवं डेटा हटाने का अधिकार**: प्रोफाइल से अपना खाता **हमेशा के लिए डिलीट (Delete)** करें।

            ### 4. संपर्क व शिकायत निवारण
            - **ईमेल**: privacy@agrisaathi.com
            - **किसान कॉल सेंटर**: **1800-180-1551** (टोल-फ्री)
            """).strip()
        )
    else:
        st.title("🛡️ Privacy Policy & Farmer Data Rights (DPDP Act, 2023)")
        st.caption("Official Compliance Policy under the Digital Personal Data Protection Act, 2023")

        st.markdown(
            textwrap.dedent("""
            ### 1. Purpose of Data Processing
            AgriSaathi AI collects and processes data solely for lawful agricultural support purposes:
            - **Localized Agronomic Advisory**: Tailoring guidance based on soil, crop stage, and weather.
            - **Mandi Price Analytics**: Comparing multi-market auction rates and transport logistics.
            - **Farm Records Management**: Maintaining private digital diaries of activities, expenses, and harvests.

            ### 2. Data Protection & Security Architecture
            - **Argon2id Password Hashing**: Zero plaintext passwords stored.
            - **Zero Third-Party Sale**: We never sell, monetize, or lease farmer personal data to commercial marketers.
            - **Tenant Isolation**: Strict authorization guards ensure no farmer can view another farmer's records.

            ### 3. Data Principal Rights (DPDP Act, 2023)
            Every farmer using AgriSaathi AI is entitled to exercise the following rights:
            - **Right to Access & Review**: View all registered personal and farm data at any time.
            - **Right to Data Portability**: Export complete farm records as machine-readable **JSON** via Profile settings.
            - **Right to Rectification**: Correct inaccurate profile, crop, or financial entries.
            - **Right to Erasure**: Permanently delete your account and cascade-delete all associated farm data.

            ### 4. Grievance Redressal
            - **Data Protection Officer**: privacy@agrisaathi.com
            - **Immediate Agricultural Support (Kisan Call Centre)**: **1800-180-1551** (Toll-Free)
            """).strip()
        )

