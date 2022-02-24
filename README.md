# html-builder
Static HTML pages generator

_Other languages: [English](https://github.com/dimaglushkov/portfolio-builder/blob/main/README.md), [Русский](https://github.com/dimaglushkov/portfolio-builder/blob/main/README.ru.md)_ 

# The way it works
There are three entities you need to configure once before running:
1. Configuration - `/config/config.yml` - general configuration file, `(/config/*.yml)` - files with attribute values, which will be used for page generation.
2. Theme - JS, CSS, and HTML-template with special variables (more details on variables below) 
3. Assets - basically any media file such as images or icons
 
## Variables and attributes
Variables mentioned above are connected through the attributes.
- In terms of configuration: attribute is a value in config YAML file. For example:
```yaml
general:
  name:
    Dima
```
- In terms of HTML-templates: attribute is a specially formatted code right inside html, which will be replaced with the value from configuration by generator. For example:
```html
<head>
    <title>%general.name%</title>
</head>
```

By now generator supports 3 types of attributes:
1. Simple attribute. Represented in HTML code as yaml variable wrapped in `%` (snippet above is the example of simple attribute). For this type of attribute generator basically replace the attribute with the value from config.
2. List-typed attribute. <br>
   - HTML representation example:
       ```html
       ;#some_list
       <div class="some_list_class">
           <a href="%url%">%name%</a>
       </div>
       ;#
       ```
   - Yaml representation example:
       ```yaml
       some_list:
         -
           url: https://example.com/1
           name: example 1
         -  
           url: https://example.com/2
           name: example 2
       ```
   For every element of the list variable (which name stated after first `;#`) in YAML file, generator will create entry from html code replacing variables with actual values. 
   - Result example:
    ```html
    <div class="some_list_class">
        <a href="https://example.com/1">example 1</a>
    </div>
    <div class="some_list_class">
        <a href="https://example.com/2">example 2</a>
    </div>
    ```
3. Conditional attribute.
   - HTML representation example: <br>
    ```html
    ?url
    <div class="some_variable">
        <a href="%url%">%name%</a>
    </div>
    ?
   
    ...
   
    <img src="example.com" ?alt_text alt="%alt_text%"?></img>
    ```
    YAML config representation of conditional attribute is identical to the simple one. Key difference is that conditional attributes can be omitted - in this case generator will just ignore it.<br>
    Usually it makes most sense to use conditional attributes inside the list-typed attributes.

## Attributes independence
Set of used attributes is defined only by used theme and limited only by your imagination. Feel free to edit existing theme or even crete your own

### Features of the default theme
- Automatically gets info about stargazers of github repos
- Multilanguage support

### Future features of the default theme
- Generating PDF with key info from the same config files
- Target environment differentiation (github pages or nginx server), for nginx cases also creating config file
