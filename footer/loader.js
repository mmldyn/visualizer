// --- [KODE HTML FOOTER LENGKAP] ---
// Kita letakkan HTML-nya di sini untuk menghindari masalah cache
const footerHTML = `
<footer class="fixed bottom-0 left-0 right-0 max-w-lg mx-auto bg-transparent">
    <div class="relative bg-white/90 backdrop-blur-sm rounded-t-3xl shadow-[0_-10px_30px_-15px_rgba(0,0,0,0.1)]">
         <div class="absolute -top-7 left-1/2 -translate-x-1/2">
            <!-- [PERUBAHAN] Mengubah <button> menjadi <a> dengan href -->
            <a id="nav-center" href="./todo.html" class="block bg-[#6F4AB0] p-4 rounded-full shadow-lg shadow-[#6F4AB0]/50 transform transition-transform duration-300 hover:scale-110">
                 <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
            </a>
            <!-- [AKHIR PERUBAHAN] -->
        </div>
        <nav class="flex justify-around items-center h-20">
            <!-- Tautan Home -->
            <a id="nav-home" href="./dashboard.html" class="nav-item transform transition-transform duration-300 hover:scale-110">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" viewBox="0 0 20 20" fill="currentColor"><path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" /></svg>
            </a>
            <!-- Tautan Course -->
            <a id="nav-course" href="./dashboard-course.html" class="nav-item transform transition-transform duration-300 hover:scale-110">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M12 14l9-5-9-5-9 5 9 5z"></path><path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-9.998 12.078 12.078 0 01.665-6.479L12 14z"></path><path stroke-linecap="round" stroke-linejoin="round" d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-9.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222 4 2.222V20M12 14.75L2 10l10-5.25L22 10l-10 4.75z"></path></svg>
            </a>
            <div class="w-12 h-12"></div> <!-- Placeholder untuk ruang tombol tengah -->
            <!-- Tautan Project -->
            <a id="nav-project" href="./project.html" class="nav-item transform transition-transform duration-300 hover:scale-110">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
            </a>
            <!-- Tautan Profile -->
            <a id="nav-profile" href="./ai_feedback.html" class="nav-item transform transition-transform duration-300 hover:scale-110">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </a>
        </nav>
    </div>
</footer>
`; // <-- PASTIKAN TANDA BACKTICK INI ADA DI AKHIR VARIABEL

// File ini akan mengambil HTML footer dan mengaturnya di halaman
function loadFooter(activePageId) {
    // Masukkan HTML footer ke dalam placeholder
    const placeholder = document.getElementById('footer-placeholder');
    if (placeholder) {
        placeholder.innerHTML = footerHTML;
    }
    
    // --- [LOGIKA PEWARNAAN IKON] ---
    
    // Dapatkan semua item navigasi
    const navItems = document.querySelectorAll('.nav-item');
    
    // 1. Hapus SEMUA kelas warna (aktif/tidak aktif) dari semua ikon
    navItems.forEach(item => {
        item.classList.remove('text-gray-500');
        item.classList.remove('text-[#6F4AB0]');
    });

    // 2. Beri warna abu-abu (default) ke SEMUA ikon
    navItems.forEach(item => {
        item.classList.add('text-gray-500');
    });

    // 3. Temukan link yang aktif
    const activeLink = document.getElementById(activePageId);
    if (activeLink) {
        // 4. Hapus warna abu-abu dan tambahkan warna ungu HANYA ke link aktif
        activeLink.classList.remove('text-gray-500');
        activeLink.classList.add('text-[#6F4AB0]');
    }
}

