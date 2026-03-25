#!/usr/bin/env python3
import os

with open('/tmp/design-fixes-current.css', 'r') as f:
    lines = f.readlines()

part1 = lines[:261]
part3 = lines[353:1555]

new_section7_text = """
/* =====================================================
   7. GALLERY - Arrows, Zoom Icon, Fullscreen Modal
   ===================================================== */
#gallery-main {
    position: relative;
}

#gallery-main::before,
#gallery-main::after {
    display: none !important;
}

.gallery-arrow {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    z-index: 20;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.85);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
    border: none;
    cursor: pointer;
    color: #555;
    opacity: 0;
    transition: opacity 0.3s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.gallery-arrow-left {
    left: 10px;
}

.gallery-arrow-right {
    right: 10px;
}

#gallery-main:hover .gallery-arrow {
    opacity: 1;
}

.gallery-arrow:hover {
    background: #fff;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.gallery-arrow:focus {
    outline: 2px solid #a9ba9d;
    outline-offset: 2px;
    opacity: 1;
}

.gallery-zoom {
    position: absolute;
    right: 12px;
    bottom: 12px;
    z-index: 20;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.85);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
    border: none;
    cursor: zoom-in;
    color: #666;
    opacity: 0;
    transition: opacity 0.3s ease;
}

#gallery-main:hover .gallery-zoom {
    opacity: 0.7;
}

.gallery-zoom:hover {
    opacity: 1;
    background: #fff;
}

.gallery-zoom:focus {
    outline: 2px solid #a9ba9d;
    outline-offset: 2px;
    opacity: 1;
}

.gallery-zoom svg {
    display: block;
    width: 20px;
    height: 20px;
}

.gallery-fullscreen-overlay {
    background: rgba(0, 0, 0, 0.85) !important;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}

.gallery-fullscreen-overlay .gallery-arrow {
    opacity: 1;
    background: rgba(255, 255, 255, 0.15);
    color: #fff;
    box-shadow: none;
}

.gallery-fullscreen-overlay .gallery-arrow:hover {
    background: rgba(255, 255, 255, 0.3);
}

.gallery-close-btn {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border: none;
    color: #fff;
    transition: background 0.2s ease, transform 0.2s ease;
}

.gallery-close-btn:hover {
    background: rgba(255, 255, 255, 0.4);
    transform: scale(1.1);
}

.gallery-close-btn:focus {
    outline: 2px solid #a9ba9d;
    outline-offset: 2px;
}

@media (min-width: 769px) {
    #gallery > div > div:first-child {
        overflow: hidden;
    }
    #gallery > div > div:first-child img {
        max-height: 720px;
        object-fit: contain;
    }
    .js_thumbs_slides {
        max-height: 720px !important;
    }
}

#gallery .gallery-thumb.active,
#gallery .gallery-thumb[aria-current="true"],
#gallery button.active img,
#gallery [data-gallery-role="nav-frame"].active {
    border-color: #a9ba9d !important;
}

"""

with open('/tmp/design-fixes-clean.css', 'w') as f:
    f.writelines(part1)
    f.write(new_section7_text)
    f.writelines(part3)

size = os.path.getsize('/tmp/design-fixes-clean.css')
with open('/tmp/design-fixes-clean.css', 'r') as f:
    total = len(f.readlines())
print(f"Created: {total} lines, {size} bytes")
