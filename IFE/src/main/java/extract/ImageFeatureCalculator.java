package extract;

import org.apache.commons.io.FileUtils;
import org.apache.commons.io.filefilter.TrueFileFilter;
import org.openimaj.image.FImage;
import org.openimaj.image.ImageUtilities;
import org.openimaj.image.MBFImage;
import org.openimaj.image.feature.global.AvgBrightness;
import org.openimaj.image.feature.global.Colorfulness;
import org.openimaj.image.feature.global.RGBRMSContrast;
import org.openimaj.image.feature.global.Sharpness;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;


public class ImageFeatureCalculator {
    public static void main(String[] args) throws IOException {
        File fpath = new File("E:/data/Final/resized_images");
        File opath = new File("E:/data/Final/openimaj-images-all.csv");

        List<File> files = (List<File>) FileUtils.listFiles(fpath, TrueFileFilter.INSTANCE, TrueFileFilter.INSTANCE);

        if (opath.exists())
            opath.delete();
        String header = "image,brightness,sharpness,colorfulness,contrast,entropy";
        writeData(header + "\n", opath, true);

        int unparsable = 0;

        for (int i = 0; i < files.size(); i++) {

            File originalImage = files.get(i);
            //if (!originalImage.getName().endsWith(".jpg"))
            //    continue;

            MBFImage image;
            FImage fImage;
            try {
                image = ImageUtilities.readMBF(originalImage);
                fImage = ImageUtilities.readF(originalImage);
            } catch (IOException e) {
                System.err.print(e);
                System.err.print(originalImage);
                writeData(originalImage + "\n", new File("E:/data/27-02-2020-14-16/unparsable.csv"), true);
                unparsable += 1;
                continue;
            }

            //Naturalness naturalnesser = new Naturalness();
            //naturalnesser.analyseImage(image);
            //double naturalness = naturalnesser.getNaturalness();

            //Saturation sat = new Saturation();
            //sat.analyseImage(image);
            //double saturation = sat.getSaturation();

            //SaturationVariation satVariationer = new SaturationVariation();
            //satVariationer.analyseImage(image);
            //double saturationVariation = satVariationer.getSaturationVariation();

            //SharpnessVariation sharpVariationer = new SharpnessVariation();
            //sharpVariationer.analyseImage(fImage);
            //double sharpnessVartiation = sharpVariationer.getSharpnessVariation();

            //RMSContrast rmsContraster = new RMSContrast();
            //rmsContraster.analyseImage(fImage);
            //double contrast = rmsContraster.getContrast();

            //avg brightness
            AvgBrightness brightnesser = new AvgBrightness();
            brightnesser.analyseImage(image);
            double brightness = brightnesser.getBrightness();

            //sharpnes
            Sharpness sharpnesser = new Sharpness();
            sharpnesser.analyseImage(fImage);
            double sharpness = sharpnesser.getSharpness();

            //contrast
            RGBRMSContrast contraster = new RGBRMSContrast();
            contraster.analyseImage(image);
            double rgbContrast = contraster.getContrast();

            Colorfulness colourfulnesser = new Colorfulness();
            for (int y = 0; y < image.getHeight(); y++) {
                for (int x = 0; x < image.getWidth(); x++) {
                    colourfulnesser.analysePixel(image.getPixel(x, y));
                }
            }

            double colourfulness = colourfulnesser.getColorfulness();

            double entropy = getShannonEntropyOfImage(fImage);

            //String printit = originalImage.getName() + "," + brightness + "," + sharpness + "," + contrast + ","
            //        + colourfulness + "," + entropy + "," + rgbContrast + "," + sharpnessVartiation + ","
            //        + saturation + "," + saturationVariation + "," + naturalness;
            String printit = originalImage.getName() + "," + brightness + "," + sharpness + "," + colourfulness + "," + rgbContrast + "," + entropy;
            // System.out.println(printit);
            // System.out.println(i + "\t out of \t" + files.size());

            writeData(printit + "\n", opath, true);

        }
    System.out.println("Could not be parsed: " + unparsable);
    }

    private static double getShannonEntropyOfImage(FImage image) {
        List<String> values = new ArrayList<>();

        int n = 0;

        Map<Float, Integer> map = new HashMap<>();

        for (int i = 0; i < image.height; i++) {

            for (int j = 0; j < image.width; j++) {

                float greyscaleValue = image.getPixel(j, i);

                if (!values.contains(String.valueOf(greyscaleValue)))
                    values.add(String.valueOf(greyscaleValue));

                if (map.containsKey(greyscaleValue)) {
                    map.put(greyscaleValue, map.get(greyscaleValue) + 1);
                } else {
                    map.put(greyscaleValue, 1);
                }
                ++n;
            }
        }

        double entropy = 0.0;
        for (Map.Entry<Float, Integer> entry : map.entrySet()) {
            double p = (double) entry.getValue() / n;
            entropy -= p * (Math.log(p) / Math.log(2));
        }

        return entropy;
    }

    public static ArrayList<File> listFiles(File fpath) {
        FileFilter fileFileFilter = new FileFilter() {
            public boolean accept(File file) {
                return file.isFile();
            }
        };

        File[] ListAsFile = fpath.listFiles(fileFileFilter);
        ArrayList<File> filesInDirectory = new ArrayList<File>(ListAsFile.length);
        filesInDirectory.addAll(Arrays.asList(ListAsFile));

        return filesInDirectory;
    }

    public static synchronized void writeData(String str, File opath, boolean append) {
        try {
            File file = opath;
            //System.err.println(file);
            // if file does not exist, then create it
            if (!file.exists()) {
                file.createNewFile();
            }
            // true = append file
            FileWriter fileWriter = new FileWriter(file, append);
            BufferedWriter bufferWriter = new BufferedWriter(fileWriter);
            bufferWriter.write(str);
            bufferWriter.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

}
