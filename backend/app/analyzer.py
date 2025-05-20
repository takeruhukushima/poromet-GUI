import porespy as ps
import numpy as np
import matplotlib.pyplot as plt
import skimage.io
from skimage.filters import threshold_otsu
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import os

class PoreAnalyzer:
    """
    Analyze pore size distribution from SEM images.
    """
    def __init__(self):
        # pixel_data: resolution -> {magnification: px_per_nm}
        self.pixel_data = {
            (2560, 1920): {10:1008/5000, 20:807/2000, 50:1022/1000, 100:1018/500},
            (1280, 960) : {200:406/200 , 300:303/100},
            (554, 416)  : {200:174/200 },
        }

    def extract_nm_per_px(self, img_path: str, magnification: int) -> float:
        """
        Get pixel size from resolution table.
        Returns nm_per_px (float).
        """
        img = skimage.io.imread(img_path, as_gray=True)
        h, w = img.shape[:2]
        try:
            px_per_nm = self.pixel_data[(w, h)][magnification]
        except KeyError:
            raise ValueError(f"未知の解像度({w}×{h})または倍率({magnification}×)")
        return 1.0 / px_per_nm

    def _calculate_radii_px(self, nm_per_px: float, max_diam_nm: int) -> list:
        """
        Generate pixel radii array for porosimetry.
        修正: 正しく px_per_nm を計算して使用する
        """
        px_per_nm = 1.0 / nm_per_px  # nm_per_px から px_per_nm を計算
        max_rad_px = int((max_diam_nm/2) * px_per_nm)  # 上限半径[px]
        return list(range(1, max_rad_px+1))

    def analyze_image(self,
                      img_path: str,
                      magnification: int = 300,
                      max_diam_nm: int = 80,
                      thresh_mag: float = 1.8) -> Dict[str, Any]:
        """
        Perform segmentation, porosimetry, and compute statistics.
        Returns:
            dict with image_info, statistics, diameter_distribution.
        """
        # Setup output
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        outdir = Path("output_data") / ts
        outdir.mkdir(parents=True, exist_ok=True)

        # Load image
        img = skimage.io.imread(img_path, as_gray=True)
        h, w = img.shape[:2]
        nm_per_px = self.extract_nm_per_px(img_path, magnification)

        # Segmentation
        th = threshold_otsu(img) * thresh_mag
        mask_pore = img < th

        # Porosimetry
        radii_px = self._calculate_radii_px(nm_per_px, max_diam_nm)
        im_thick = ps.filters.porosimetry(mask_pore, sizes=radii_px)
        psd = ps.metrics.pore_size_distribution(
            im_thick, log=False, bins=100, voxel_size=nm_per_px
        )

        # Statistics (all in nm units)
        avg_rad_nm = np.average(psd.bin_centers, weights=psd.pdf)
        avg_diam_nm = 2 * avg_rad_nm
        mode_rad_nm = psd.bin_centers[np.argmax(psd.pdf)]
        mode_diam_nm = 2 * mode_rad_nm

        # Debug prints
        print(f"Debug: avg_rad_nm = {avg_rad_nm}, mode_rad_nm = {mode_rad_nm}")
        
        # Convert to diameter scale
        diam_centers = psd.bin_centers * 2
        diam_widths = psd.bin_widths * 2
        diam_pdf = psd.pdf / 2

        results = {
            'image_info': {
                'dimensions': f"{w}×{h}px",
                'pixel_size': f"{nm_per_px:.3f} nm/px",
                'magnification': f"{magnification}×"
            },
            'statistics': {
                'average_diameter': f"{avg_diam_nm:.3f} nm",
                'mode_diameter': f"{mode_diam_nm:.3f} nm"
            },
            'diameter_distribution': {
                'centers': diam_centers.tolist(),
                'widths': diam_widths.tolist(),
                'pdf': diam_pdf.tolist()
            }
        }

        # Save and return
        self.save_results(outdir, results, mask_pore, im_thick)
        return results, mask_pore, im_thick

    def save_results(self,
                     outdir: Path,
                     results: Dict[str, Any],
                     mask: np.ndarray,
                     im_thick: np.ndarray) -> None:
        """
        Save text report, histogram, mask, and porosity map.
        """
        # Text report
        txt = outdir / "pore_size_analysis.txt"
        with open(txt, "w") as f:
            f.write("Pore Size Analysis (all nm units)\n")
            info = results['image_info']
            f.write(f"Image : {info['dimensions']} , {info['magnification']}\n")
            f.write(f"Pixel  : {info['pixel_size']}\n\n")
            stats = results['statistics']
            f.write(f"Average Diameter : {stats['average_diameter']}\n")
            f.write(f"Mode    Diameter : {stats['mode_diameter']}\n\n")
            f.write("Diameter_center(nm)\tBin_width(nm)\tPDF_diameter\n")
            dd = results['diameter_distribution']
            for c, w_, p in zip(dd['centers'], dd['widths'], dd['pdf']):
                f.write(f"{c:.3f}\t{w_:.3f}\t{p:.6f}\n")

        # Histogram figure
        fig, ax = plt.subplots(figsize=(8,6))
        dd = results['diameter_distribution']
        ax.bar(dd['centers'], dd['pdf'], width=dd['widths'], edgecolor='k')
        ax.set(xlabel='Pore Diameter (nm)', 
               ylabel='Probability Density', 
               title='Pore Size Distribution (diameter)')
        plt.tight_layout()
        fig.savefig(outdir / "pore_size_distribution.png")
        plt.close(fig)

        # RAW histogram data
        raw = outdir / "raw_histogram_data.txt"
        with open(raw, "w") as f:
            f.write("Diameter_center(nm)\tPDF_diameter\n")
            dd = results['diameter_distribution']
            for c, p in zip(dd['centers'], dd['pdf']):
                f.write(f"{c:.3f}\t{p:.6f}\n")
            # Calculate and save weighted mean diameter
            mean_diam_nm = np.average(dd['centers'], weights=dd['pdf'])
            f.write(f"\nWeighted Mean Diameter: {mean_diam_nm:.3f} nm\n")

        # Save diagnostic images
        # 1. Thresholded binary image
        skimage.io.imsave(
            str(outdir / "thresholded_image.png"),
            (mask.astype(np.uint8) * 255)
        )
        # 2. Filtered image with colormap
        plt.imsave(
            str(outdir / "filtered_image_colormap.png"),
            im_thick,
            cmap="viridis"
        )
        
        print(f"Results saved under: {outdir}")

# Instantiate for import
analyzer = PoreAnalyzer()