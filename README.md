# mitsuba examples scenes

all scenes come from web, mainly [sketchfab](https://sketchfab.com/), exported with blender and rendered with [mitsuba 2](https://github.com/mitsuba-renderer/mitsuba2)

some showcase here

## higokumaru

[model link]:https://sketchfab.com/3d-models/higokumaru-honkai-impact-3rd-0e903387170846f5939adaa0c277b91b

the texture of the model has light effect (self shadows) on it, so when rendered again this will appear a little dark, especially the white cloth, or maybe there is something wrong with the light settings. 

<img src="images/higokumaru.png" style="zoom:50%;" />

## psyduck

[model link]: https://sketchfab.com/3d-models/psyduck-6bd718edee504a26922000c546a455a9

confused psyduck, just like me when looking at mitsuba2's code

<img src="images/psyduck.png" style="zoom:50%;" />

## xml-validation

this reporsitory also contains a xml-model to validate xml file of mitsuba scenes, to use it

1. make sure your text editor has a functionality to perform xml validation(for my case, vs code + xml plugin is enough)

2. copy the `mitsuba.xsd` to your scene path, and add the following code before your scene tag

   ```xml
   <?xml-model href="$path-to-your-mitsuba.xsd"?>
   <scene version='2.2.1'>
       ...
   </scene>
   ```

3. then, as usual, use `mitsuba -m scalar_spectral xxx.xml` to render a scene

## License

<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt="Creative Commons License" style="border-width:0" src="images/88x31-20220713140959838.png" /></a><br />All scenes are licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Attribution-NonCommercial 4.0 International License</a>.
