import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Elektrikli Şarj İstasyonu Analiz Sistemi",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stilleri
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-card {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .danger-card {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Veri oluşturma fonksiyonları
@st.cache_data
def generate_charging_stations():
    """Türkiye'deki şarj istasyonları için örnek veri oluştur"""
    cities = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana", "Konya", "Gaziantep", "Mersin", "Kayseri"]
    operators = ["Zorlu Enerji", "Aksa Enerji", "Şarj Noktası", "ePark", "Voltrun", "Tesla Supercharger"]
    power_types = ["AC 22kW", "DC 50kW", "DC 150kW", "DC 350kW"]
    
    data = []
    for i in range(250):
        city = np.random.choice(cities)
        lat_base = {
            "İstanbul": 41.0082, "Ankara": 39.9334, "İzmir": 38.4192,
            "Bursa": 40.1826, "Antalya": 36.8969, "Adana": 37.0000,
            "Konya": 37.8746, "Gaziantep": 37.0662, "Mersin": 36.8000,
            "Kayseri": 38.7312
        }
        lng_base = {
            "İstanbul": 28.9784, "Ankara": 32.8597, "İzmir": 27.1287,
            "Bursa": 29.0669, "Antalya": 30.7133, "Adana": 35.3213,
            "Konya": 32.4932, "Gaziantep": 37.3833, "Mersin": 34.6414,
            "Kayseri": 35.4787
        }
        
        data.append({
            "istasyon_id": f"ST{i+1:03d}",
            "isim": f"{np.random.choice(operators)} - {city} {i%10+1}",
            "sehir": city,
            "operatör": np.random.choice(operators),
            "güç_tipi": np.random.choice(power_types),
            "güç_kw": int(np.random.choice(power_types).split()[1].replace("kW", "")),
            "soket_sayisi": np.random.randint(2, 12),
            "lat": lat_base[city] + np.random.uniform(-0.3, 0.3),
            "lng": lng_base[city] + np.random.uniform(-0.3, 0.3),
            "kullanim_orani": np.random.uniform(0.3, 0.9),
            "gunluk_gelir": np.random.uniform(500, 3000),
            "kurulum_tarihi": datetime.now() - timedelta(days=np.random.randint(30, 1095))
        })
    
    return pd.DataFrame(data)

@st.cache_data
def generate_demographic_data():
    """Demografik veriler oluştur"""
    cities = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana", "Konya", "Gaziantep", "Mersin", "Kayseri"]
    data = []
    
    for city in cities:
        data.append({
            "sehir": city,
            "nufus": np.random.randint(500000, 15000000),
            "ortalama_gelir": np.random.randint(35000, 85000),
            "ev_sayisi": np.random.randint(200000, 6000000),
            "trafik_yogunlugu": np.random.uniform(0.4, 0.95),
            "elektrikli_arac_orani": np.random.uniform(0.02, 0.08),
            "potansiyel_puan": np.random.uniform(3.5, 9.2)
        })
    
    return pd.DataFrame(data)

def calculate_roi(investment, monthly_revenue, operating_cost, years=5):
    """Yatırım getirisi hesapla"""
    annual_revenue = monthly_revenue * 12
    annual_profit = annual_revenue - operating_cost
    total_profit = annual_profit * years
    roi = ((total_profit - investment) / investment) * 100
    payback_period = investment / annual_profit
    
    return {
        "roi": roi,
        "payback_period": payback_period,
        "annual_profit": annual_profit,
        "total_profit": total_profit
    }

def analyze_location(lat, lng, stations_df, demographic_df):
    """Seçilen lokasyonu analiz et"""
    # Yakındaki istasyonları bul
    distances = np.sqrt((stations_df['lat'] - lat)**2 + (stations_df['lng'] - lng)**2)
    nearby_stations = stations_df[distances < 0.1]  # ~10km yakınındaki istasyonlar
    
    # En yakın şehri bul
    city_centers = {
        "İstanbul": (41.0082, 28.9784), "Ankara": (39.9334, 32.8597),
        "İzmir": (38.4192, 27.1287), "Bursa": (40.1826, 29.0669),
        "Antalya": (36.8969, 30.7133), "Adana": (37.0000, 35.3213),
        "Konya": (37.8746, 32.4932), "Gaziantep": (37.0662, 37.3833),
        "Mersin": (36.8000, 34.6414), "Kayseri": (38.7312, 35.4787)
    }
    
    min_distance = float('inf')
    closest_city = None
    for city, (city_lat, city_lng) in city_centers.items():
        distance = np.sqrt((lat - city_lat)**2 + (lng - city_lng)**2)
        if distance < min_distance:
            min_distance = distance
            closest_city = city
    
    # Demografik veriyi al
    demo_data = demographic_df[demographic_df['sehir'] == closest_city].iloc[0] if closest_city else None
    
    # Rekabet analizi
    competition_score = len(nearby_stations)
    if competition_score == 0:
        competition_level = "Düşük"
    elif competition_score < 3:
        competition_level = "Orta"
    else:
        competition_level = "Yüksek"
    
    # Potansiyel puan hesapla
    if demo_data is not None:
        potential_score = (
            demo_data['potansiyel_puan'] * 0.4 +
            (10 - competition_score) * 0.3 +
            demo_data['trafik_yogunlugu'] * 10 * 0.3
        )
    else:
        potential_score = 5.0
    
    return {
        "closest_city": closest_city,
        "nearby_stations": len(nearby_stations),
        "competition_level": competition_level,
        "potential_score": round(potential_score, 1),
        "demographic_data": demo_data
    }

# Ana uygulama
def main():
    st.markdown('<h1 class="main-header">⚡ Elektrikli Şarj İstasyonu Analiz Sistemi</h1>', unsafe_allow_html=True)
    
    # Veri yükleme
    stations_df = generate_charging_stations()
    demographic_df = generate_demographic_data()
    
    # Sidebar - Kullanıcı tipi seçimi
    st.sidebar.title("🎯 Kullanıcı Modu")
    user_type = st.sidebar.selectbox(
        "Lütfen kullanıcı tipinizi seçin:",
        ["Genel Kullanıcı", "Yatırımcı"]
    )
    
    if user_type == "Genel Kullanıcı":
        show_general_user_interface(stations_df, demographic_df)
    else:
        show_investor_interface(stations_df, demographic_df)

def show_general_user_interface(stations_df, demographic_df):
    """Genel kullanıcı arayüzü"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Genel Kullanıcı Özellikleri")
    
    tab1, tab2, tab3 = st.tabs(["🗺️ Şarj İstasyonu Haritası", "📈 İstatistikler", "👥 Demografik Analiz"])
    
    with tab1:
        st.header("🗺️ Türkiye Şarj İstasyonu Haritası")
        
        # Filtreler
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_cities = st.multiselect(
                "Şehir Seçin:",
                options=stations_df['sehir'].unique(),
                default=stations_df['sehir'].unique()[:3]
            )
        
        with col2:
            selected_operators = st.multiselect(
                "Operatör Seçin:",
                options=stations_df['operatör'].unique(),
                default=stations_df['operatör'].unique()
            )
        
        with col3:
            power_range = st.slider(
                "Güç Aralığı (kW):",
                min_value=int(stations_df['güç_kw'].min()),
                max_value=int(stations_df['güç_kw'].max()),
                value=(int(stations_df['güç_kw'].min()), int(stations_df['güç_kw'].max()))
            )
        
        # Filtreleme
        filtered_stations = stations_df[
            (stations_df['sehir'].isin(selected_cities)) &
            (stations_df['operatör'].isin(selected_operators)) &
            (stations_df['güç_kw'] >= power_range[0]) &
            (stations_df['güç_kw'] <= power_range[1])
        ]
        
        # Harita oluştur
        m = folium.Map(location=[39.9334, 32.8597], zoom_start=6)
        
        # Operatör renkleri
        operator_colors = {
            "Zorlu Enerji": "red",
            "Aksa Enerji": "blue", 
            "Şarj Noktası": "green",
            "ePark": "purple",
            "Voltrun": "orange",
            "Tesla Supercharger": "darkred"
        }
        
        for _, station in filtered_stations.iterrows():
            folium.Marker(
                [station['lat'], station['lng']],
                popup=f"""
                <b>{station['isim']}</b><br>
                Operatör: {station['operatör']}<br>
                Güç: {station['güç_tipi']}<br>
                Soket: {station['soket_sayisi']}<br>
                Kullanım: %{station['kullanim_orani']:.0%}
                """,
                tooltip=station['isim'],
                icon=folium.Icon(color=operator_colors.get(station['operatör'], 'gray'))
            ).add_to(m)
        
        st_folium(m, width=700, height=500)
        
        # İstatistikler
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Toplam İstasyon", len(filtered_stations))
        with col2:
            st.metric("Toplam Soket", filtered_stations['soket_sayisi'].sum())
        with col3:
            st.metric("Ortalama Güç", f"{filtered_stations['güç_kw'].mean():.0f} kW")
        with col4:
            st.metric("Ortalama Kullanım", f"%{filtered_stations['kullanim_orani'].mean():.0%}")
    
    with tab2:
        st.header("📈 Şarj İstasyonu İstatistikleri")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Operatör dağılımı
            operator_dist = stations_df['operatör'].value_counts()
            fig_pie = px.pie(
                values=operator_dist.values,
                names=operator_dist.index,
                title="Operatör Dağılımı"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Güç dağılımı
            fig_power = px.histogram(
                stations_df,
                x='güç_kw',
                title="Güç Dağılımı",
                nbins=20
            )
            st.plotly_chart(fig_power, use_container_width=True)
        
        with col2:
            # Şehir bazında istasyon sayısı
            city_dist = stations_df['sehir'].value_counts()
            fig_bar = px.bar(
                x=city_dist.index,
                y=city_dist.values,
                title="Şehir Bazında İstasyon Sayısı"
            )
            fig_bar.update_xaxis(tickangle=45)
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Kullanım oranı dağılımı
            fig_usage = px.histogram(
                stations_df,
                x='kullanim_orani',
                title="Kullanım Oranı Dağılımı",
                nbins=20
            )
            st.plotly_chart(fig_usage, use_container_width=True)
    
    with tab3:
        st.header("👥 Demografik Analiz")
        
        # Demografik veriler tablosu
        st.subheader("Şehir Bazında Demografik Veriler")
        
        # Verileri formatla
        demo_display = demographic_df.copy()
        demo_display['nufus'] = demo_display['nufus'].apply(lambda x: f"{x:,}")
        demo_display['ortalama_gelir'] = demo_display['ortalama_gelir'].apply(lambda x: f"₺{x:,}")
        demo_display['ev_sayisi'] = demo_display['ev_sayisi'].apply(lambda x: f"{x:,}")
        demo_display['trafik_yogunlugu'] = demo_display['trafik_yogunlugu'].apply(lambda x: f"%{x:.0%}")
        demo_display['elektrikli_arac_orani'] = demo_display['elektrikli_arac_orani'].apply(lambda x: f"%{x:.1%}")
        demo_display['potansiyel_puan'] = demo_display['potansiyel_puan'].apply(lambda x: f"{x:.1f}/10")
        
        st.dataframe(
            demo_display,
            column_config={
                "sehir": "Şehir",
                "nufus": "Nüfus",
                "ortalama_gelir": "Ortalama Gelir",
                "ev_sayisi": "Ev Sayısı",
                "trafik_yogunlugu": "Trafik Yoğunluğu",
                "elektrikli_arac_orani": "EV Oranı",
                "potansiyel_puan": "Potansiyel Puanı"
            },
            use_container_width=True
        )
        
        # Görselleştirmeler
        col1, col2 = st.columns(2)
        
        with col1:
            fig_scatter = px.scatter(
                demographic_df,
                x='ortalama_gelir',
                y='elektrikli_arac_orani',
                size='nufus',
                color='potansiyel_puan',
                hover_name='sehir',
                title="Gelir vs EV Oranı (Nüfus Boyutu)"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with col2:
            fig_potential = px.bar(
                demographic_df.sort_values('potansiyel_puan', ascending=True),
                x='potansiyel_puan',
                y='sehir',
                orientation='h',
                title="Şehir Potansiyel Puanları"
            )
            st.plotly_chart(fig_potential, use_container_width=True)

def show_investor_interface(stations_df, demographic_df):
    """Yatırımcı arayüzü"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💼 Yatırımcı Özellikleri")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Bölge Analizi", "🏆 Rakip Analizi", "💰 Yatırım Getirisi", "📋 Rapor Oluştur"])
    
    with tab1:
        st.header("🎯 Lokasyon Analizi")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Harita Üzerinde Konum Seçin")
            
            # Harita oluştur
            m = folium.Map(location=[39.9334, 32.8597], zoom_start=6)
            
            # Mevcut istasyonları ekle
            for _, station in stations_df.iterrows():
                folium.CircleMarker(
                    [station['lat'], station['lng']],
                    radius=5,
                    popup=f"{station['isim']}",
                    color='blue',
                    fill=True,
                    fillOpacity=0.6
                ).add_to(m)
            
            # Kullanıcının seçeceği nokta için tıklama eventi
            map_data = st_folium(m, width=700, height=500)
            
            selected_location = None
            if map_data['last_object_clicked_popup']:
                st.info("Mevcut bir istasyonu seçtiniz. Yeni bir nokta seçmek için haritada boş bir alana tıklayın.")
            elif map_data['last_clicked']:
                selected_location = map_data['last_clicked']
                st.success(f"Seçilen konum: {selected_location['lat']:.4f}, {selected_location['lng']:.4f}")
        
        with col2:
            st.subheader("Analiz Sonuçları")
            
            if selected_location:
                lat, lng = selected_location['lat'], selected_location['lng']
                analysis = analyze_location(lat, lng, stations_df, demographic_df)
                
                # Potansiyel skoru
                if analysis['potential_score'] >= 7:
                    st.markdown(f'<div class="success-card"><h4>🟢 Yüksek Potansiyel</h4><p>Puan: {analysis["potential_score"]}/10</p></div>', unsafe_allow_html=True)
                elif analysis['potential_score'] >= 5:
                    st.markdown(f'<div class="warning-card"><h4>🟡 Orta Potansiyel</h4><p>Puan: {analysis["potential_score"]}/10</p></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="danger-card"><h4>🔴 Düşük Potansiyel</h4><p>Puan: {analysis["potential_score"]}/10</p></div>', unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Detaylı bilgiler
                st.markdown("**📍 Konum Bilgileri:**")
                st.write(f"• En yakın şehir: {analysis['closest_city']}")
                st.write(f"• Yakındaki istasyon sayısı: {analysis['nearby_stations']}")
                st.write(f"• Rekabet seviyesi: {analysis['competition_level']}")
                
                if analysis['demographic_data'] is not None:
                    demo = analysis['demographic_data']
                    st.markdown("**👥 Demografik Veriler:**")
                    st.write(f"• Nüfus: {demo['nufus']:,}")
                    st.write(f"• Ortalama gelir: ₺{demo['ortalama_gelir']:,}")
                    st.write(f"• EV oranı: %{demo['elektrikli_arac_orani']:.1%}")
                    st.write(f"• Trafik yoğunluğu: %{demo['trafik_yogunlugu']:.0%}")
                
                # Öneriler
                st.markdown("**💡 Öneriler:**")
                if analysis['potential_score'] >= 7:
                    st.success("✅ Bu lokasyon yatırım için çok uygun!")
                    st.write("• Hemen yatırım planlaması yapabilirsiniz")
                    st.write("• Yüksek DC güçlü istasyon önerilir")
                elif analysis['potential_score'] >= 5:
                    st.warning("⚠️ Bu lokasyon dikkatli değerlendirme gerektirir")
                    st.write("• Detaylı pazar araştırması yapın")
                    st.write("• Orta güçlü istasyonla başlayın")
                else:
                    st.error("❌ Bu lokasyon için yatırım önerilmez")
                    st.write("• Alternatif lokasyonları değerlendirin")
                    st.write("• Pazar gelişimini bekleyin")
            else:
                st.info("Analiz için harita üzerinde bir konum seçin.")
    
    with tab2:
        st.header("🏆 Rakip Analizi")
        
        # Operatör performans analizi
        operator_analysis = stations_df.groupby('operatör').agg({
            'istasyon_id': 'count',
            'soket_sayisi': 'sum',
            'güç_kw': 'mean',
            'kullanim_orani': 'mean',
            'gunluk_gelir': 'mean'
        }).round(2)
        
        operator_analysis.columns = ['İstasyon Sayısı', 'Toplam Soket', 'Ort. Güç (kW)', 'Ort. Kullanım', 'Ort. Günlük Gelir']
        
        st.subheader("Operatör Performans Tablosu")
        st.dataframe(operator_analysis, use_container_width=True)
        
        # Görselleştirmeler
        col1, col2 = st.columns(2)
        
        with col1:
            # Pazar payı
            market_share = stations_df['operatör'].value_counts()
            fig_market = px.pie(
                values=market_share.values,
                names=market_share.index,
                title="Pazar Payı (İstasyon Sayısı)"
            )
            st.plotly_chart(fig_market, use_container_width=True)
            
        with col2:
            # Gelir karşılaştırması
            fig_revenue = px.bar(
                x=operator_analysis.index,
                y=operator_analysis['Ort. Günlük Gelir'],
                title="Operatör Bazında Ortalama Günlük Gelir"
            )
            fig_revenue.update_xaxis(tickangle=45)
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        # SWOT Analizi
        st.subheader("🎯 Pazar Fırsatları")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="success-card">
            <h4>🟢 Güçlü Yönler</h4>
            <ul>
            <li>Artan EV satışları</li>
            <li>Devlet teşvikleri</li>
            <li>Çevre bilinci</li>
            <li>Teknoloji gelişimi</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="warning-card">
            <h4>🟡 Fırsatlar</h4>
            <ul>
            <li>Yeni şehirler</li>
            <li>Hızlı şarj teknolojisi</li>
            <li>Mobil uygulamalar</li>
            <li>Enerji depolama</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="danger-card">
            <h4>🔴 Tehditler</h4>
            <ul>
            <li>Yoğun rekabet</li>
            <li>Düzenleyici değişiklikler</li>
            <li>Teknoloji eskimesi</li>
            <li>Elektrik maliyetleri</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.header("💰 Yatırım Getirisi Hesaplayıcı")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Yatırım Parametreleri")
            
            # Yatırım parametreleri
            station_type = st.selectbox(
                "İstasyon Tipi:",
                ["AC 22kW (Orta)", "DC 50kW (Hızlı)", "DC 150kW (Ultra Hızlı)", "DC 350kW (Süper Hızlı)"]
            )
            
            num_sockets = st.slider("Soket Sayısı:", 2, 12, 4)
            
            # Yatırım maliyetleri (istasyon tipine göre)
            investment_costs = {
                "AC 22kW (Orta)": 50000,
                "DC 50kW (Hızlı)": 150000,
                "DC 150kW (Ultra Hızlı)": 300000,
                "DC 350kW (Süper Hızlı)": 500000
            }
            
            base_investment = investment_costs[station_type]
            total_investment = base_investment + (num_sockets - 2) * 25000
            
            st.metric("Toplam Yatırım:", f"₺{total_investment:,}")
            
            # Gelir parametreleri
            st.subheader("Gelir Parametreleri")
            
            daily_usage_hours = st.slider("Günlük Kullanım Saati:", 1, 24, 8)
            price_per_kwh = st.slider("kWh Başına Fiyat (₺):", 3.0, 15.0, 7.5)
            
            # Maliyetler
            st.subheader("İşletme Maliyetleri")
            monthly_electricity_cost = st.number_input("Aylık Elektrik Maliyeti (₺):", 5000, 50000, 15000)
            monthly_maintenance = st.number_input("Aylık Bakım Maliyeti (₺):", 2000, 20000, 5000)
            monthly_rent = st.number_input("Aylık Kira/Arsa Maliyeti (₺):", 5000, 50000, 12000)
        
        with col2:
            st.subheader("📊 Finansal Projeksiyonlar")
            
            # Güç hesaplaması
            power_kw = int(station_type.split()[1].replace("kW", ""))
            
            # Günlük gelir hesaplama
            daily_energy = power_kw * daily_usage_hours * num_sockets * 0.7  # %70 verimlilik
            daily_revenue = daily_energy * price_per_kwh
            monthly_revenue = daily_revenue * 30
            
            # İşletme maliyetleri
            total_monthly_cost = monthly_electricity_cost + monthly_maintenance + monthly_rent
            monthly_profit = monthly_revenue - total_monthly_cost
            
            # ROI hesaplama
            roi_data = calculate_roi(
                investment=total_investment,
                monthly_revenue=monthly_revenue,
                operating_cost=total_monthly_cost,
                years=5
            )
            
            # Metrikleri göster
            col2_1, col2_2 = st.columns(2)
            
            with col2_1:
                st.metric("Aylık Gelir", f"₺{monthly_revenue:,.0f}")
                st.metric("Aylık Maliyet", f"₺{total_monthly_cost:,.0f}")
                st.metric("Aylık Kar", f"₺{monthly_profit:,.0f}")
            
            with col2_2:
                st.metric("5 Yıllık ROI", f"%{roi_data['roi']:.1f}")
                st.metric("Geri Ödeme Süresi", f"{roi_data['payback_period']:.1f} yıl")
                st.metric("Yıllık Kar", f"₺{roi_data['annual_profit']:,.0f}")
            
            # Finansal grafik
            years = list(range(1, 6))
            cumulative_profit = [roi_data['annual_profit'] * year - total_investment for year in years]
            
            fig_roi = go.Figure()
            fig_roi.add_trace(go.Scatter(
                x=years,
                y=cumulative_profit,
                mode='lines+markers',
                name='Kümülatif Kar',
                line=dict(color='green', width=3)
            ))
            fig_roi.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Başabaş Noktası")
            fig_roi.update_layout(
                title="5 Yıllık Kar Projeksiyonu",
                xaxis_title="Yıl",
                yaxis_title="Kümülatif Kar (₺)",
                showlegend=False
            )
            st.plotly_chart(fig_roi, use_container_width=True)
            
            # Senaryo analizi
            st.subheader("🎯 Senaryo Analizi")
            
            scenarios = {
                "Kötümser": 0.7,
                "Gerçekçi": 1.0,
                "İyimser": 1.3
            }
            
            scenario_data = []
            for scenario, multiplier in scenarios.items():
                scenario_revenue = monthly_revenue * multiplier
                scenario_profit = scenario_revenue - total_monthly_cost
                scenario_roi = calculate_roi(total_investment, scenario_revenue, total_monthly_cost, 5)
                
                scenario_data.append({
                    "Senaryo": scenario,
                    "Aylık Gelir": f"₺{scenario_revenue:,.0f}",
                    "Aylık Kar": f"₺{scenario_profit:,.0f}",
                    "ROI (5 yıl)": f"%{scenario_roi['roi']:.1f}",
                    "Geri Ödeme": f"{scenario_roi['payback_period']:.1f} yıl"
                })
            
            scenario_df = pd.DataFrame(scenario_data)
            st.dataframe(scenario_df, use_container_width=True, hide_index=True)
            
            # Yatırım önerisi
            if roi_data['roi'] > 50:
                st.markdown("""
                <div class="success-card">
                <h4>🟢 Yatırım Önerisi: ÇOK UYGUN</h4>
                <p>Yüksek getiri oranı ile çok cazip bir yatırım fırsatı!</p>
                </div>
                """, unsafe_allow_html=True)
            elif roi_data['roi'] > 20:
                st.markdown("""
                <div class="warning-card">
                <h4>🟡 Yatırım Önerisi: UYGUN</h4>
                <p>Makul getiri oranı ile değerlendirilebilir bir yatırım.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="danger-card">
                <h4>🔴 Yatırım Önerisi: RİSKLİ</h4>
                <p>Düşük getiri oranı, alternatif lokasyonları değerlendirin.</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab4:
        st.header("📋 Detaylı Analiz Raporu")
        
        # Rapor parametreleri
        col1, col2 = st.columns(2)
        
        with col1:
            report_city = st.selectbox("Rapor için şehir seçin:", demographic_df['sehir'].unique())
            report_type = st.selectbox("Rapor tipi:", ["Özet Rapor", "Detaylı Rapor", "Yatırımcı Sunumu"])
        
        with col2:
            include_maps = st.checkbox("Harita ekle", True)
            include_financials = st.checkbox("Finansal analiz ekle", True)
        
        if st.button("📊 Rapor Oluştur", type="primary"):
            st.markdown("---")
            
            # Rapor başlığı
            st.markdown(f"""
            # 📋 {report_city} Elektrikli Şarj İstasyonu Analiz Raporu
            
            **Rapor Tarihi:** {datetime.now().strftime('%d.%m.%Y')}  
            **Rapor Tipi:** {report_type}  
            **Hazırlayan:** EV Charging Analytics System
            """)
            
            # Özet bilgiler
            city_data = demographic_df[demographic_df['sehir'] == report_city].iloc[0]
            city_stations = stations_df[stations_df['sehir'] == report_city]
            
            st.markdown("## 📊 Özet Bilgiler")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mevcut İstasyon", len(city_stations))
            with col2:
                st.metric("Toplam Soket", city_stations['soket_sayisi'].sum() if len(city_stations) > 0 else 0)
            with col3:
                st.metric("Nüfus", f"{city_data['nufus']:,}")
            with col4:
                st.metric("Potansiyel Puan", f"{city_data['potansiyel_puan']:.1f}/10")
            
            # Pazar analizi
            st.markdown("## 🎯 Pazar Analizi")
            
            st.markdown(f"""
            **{report_city}** şehri elektrikli şarj istasyonu yatırımı için aşağıdaki özelliklere sahiptir:
            
            - **Nüfus:** {city_data['nufus']:,} kişi
            - **Ortalama Gelir:** ₺{city_data['ortalama_gelir']:,}
            - **Elektrikli Araç Oranı:** %{city_data['elektrikli_arac_orani']:.1%}
            - **Trafik Yoğunluğu:** %{city_data['trafik_yogunlugu']:.0%}
            - **Mevcut İstasyon Sayısı:** {len(city_stations)}
            """)
            
            # Rekabet analizi
            if len(city_stations) > 0:
                st.markdown("## 🏆 Rekabet Durumu")
                
                operator_dist = city_stations['operatör'].value_counts()
                leading_operator = operator_dist.index[0]
                market_leader_share = (operator_dist.iloc[0] / len(city_stations)) * 100
                
                st.markdown(f"""
                - **Pazar Lideri:** {leading_operator} (%{market_leader_share:.1f} pazar payı)
                - **Ortalama İstasyon Gücü:** {city_stations['güç_kw'].mean():.0f} kW
                - **Ortalama Kullanım Oranı:** %{city_stations['kullanim_orani'].mean():.0%}
                - **Ortalama Günlük Gelir:** ₺{city_stations['gunluk_gelir'].mean():,.0f}
                """)
                
                # Operatör dağılımı grafiği
                if len(operator_dist) > 1:
                    fig_operators = px.pie(
                        values=operator_dist.values,
                        names=operator_dist.index,
                        title=f"{report_city} - Operatör Dağılımı"
                    )
                    st.plotly_chart(fig_operators, use_container_width=True)
            
            # SWOT Analizi
            st.markdown("## 🎯 SWOT Analizi")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 💪 Güçlü Yönler
                - Yüksek nüfus yoğunluğu
                - Gelişen EV pazarı
                - Devlet teşvikleri
                - Çevre bilinci artışı
                
                ### ⚠️ Zayıf Yönler
                - Yüksek ilk yatırım maliyeti
                - Teknoloji bağımlılığı
                - Elektrik maliyetleri
                - Mevzuat belirsizlikleri
                """)
            
            with col2:
                st.markdown("""
                ### 🚀 Fırsatlar
                - Artan EV satışları
                - Hızlı şarj teknolojileri
                - Akıllı şehir projeleri
                - Turizm potansiyeli
                
                ### ⚡ Tehditler
                - Yoğun rekabet
                - Teknoloji eskimesi
                - Düzenleyici değişiklikler
                - Ekonomik dalgalanmalar
                """)
            
            # Finansal öngörüler (eğer seçildiyse)
            if include_financials:
                st.markdown("## 💰 Finansal Öngörüler")
                
                # Örnek yatırım senaryosu
                example_investment = 200000  # 200K TL
                example_monthly_revenue = 45000  # 45K TL/ay
                example_monthly_cost = 25000  # 25K TL/ay
                
                example_roi = calculate_roi(example_investment, example_monthly_revenue, example_monthly_cost, 5)
                
                st.markdown(f"""
                **Örnek Yatırım Senaryosu (DC 50kW, 4 Soket):**
                - **İlk Yatırım:** ₺{example_investment:,}
                - **Aylık Gelir:** ₺{example_monthly_revenue:,}
                - **Aylık Maliyet:** ₺{example_monthly_cost:,}
                - **Aylık Net Kar:** ₺{example_monthly_revenue - example_monthly_cost:,}
                - **5 Yıllık ROI:** %{example_roi['roi']:.1f}
                - **Geri Ödeme Süresi:** {example_roi['payback_period']:.1f} yıl
                """)
            
            # Öneriler
            st.markdown("## 💡 Öneriler ve Sonuç")
            
            if city_data['potansiyel_puan'] >= 7:
                recommendation = "YÜksek potansiyelli bir lokasyon. Yatırım için uygun."
                color = "success"
            elif city_data['potansiyel_puan'] >= 5:
                recommendation = "Orta potansiyelli lokasyon. Dikkatli değerlendirme gerekli."
                color = "warning"
            else:
                recommendation = "Düşük potansiyelli lokasyon. Alternatif arayın."
                color = "danger"
            
            st.markdown(f"""
            <div class="{color}-card">
            <h4>🎯 Genel Değerlendirme</h4>
            <p>{recommendation}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            ### 📋 Eylem Planı:
            1. **Detaylı saha araştırması** yapın
            2. **Yerel yönetimlerle görüşün** (izin ve teşvikler için)
            3. **Elektrik şebekesi kapasitesini** kontrol edin
            4. **Arsa/kira anlaşmalarını** değerlendirin
            5. **Finansman seçeneklerini** araştırın
            6. **Teknik altyapı gereksinimlerini** planlayın
            """)
            
            # Rapor indirme butonu (simüle)
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("📄 PDF Olarak İndir", type="secondary"):
                    st.success("Rapor PDF formatında hazırlandı! (Demo amaçlı)")

if __name__ == "__main__":
    main()
