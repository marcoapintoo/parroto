# !/usr/bin/python
# coding=utf-8
__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys
import colorsys

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../"))

from parroto.base import multimethod, is_a


class Color(object):
    """
    Store and allow to operate with colors.
    Code based on Chroma's Color project.
    """
    color = None
    _alpha = None
    modifiers = None
    named_colors = {}
    _format_convert = {
        "rgb": "rgb256",
        "uniformed_rgb": "linear_rgb",
        "uniformed-rgb": "linear_rgb",
        "linear-rgb": "linear_rgb",
        "html": "hex",
    }

    _modifiers_convert = {
        "light": "lighter",
        "lightness": "lighter",
        "dark": "darker",
        "darkness": "darker",
        "transparent": "alpha",
        "transparency": "alpha",
        "percentage": "proportion"
    }

    def __init__(self, color_value='#FFFFFF', color_type='hex'):
        # self.color is main storage for color format (tuple in RGB float form)
        # HEX input takes string, RGB / HLS / HSV take tuples
        self.color = (1.0, 1.0, 1.0)

        # If alpha is None, it is unset and assumed to be RGB
        # If non-negative, it has been set and use RGBA, HLSA, etc
        # _alpha used internally
        self._alpha = None

        self.modifiers = {}
        color_type = color_type.lower()
        color_type = self._format_convert.get(color_type, color_type)
        self.set_value(color_value, color_type)

    @multimethod()
    def set_value(self, value, color_type):
        color_type = color_type.lower()
        color_fixed = self._format_convert.get(color_type, color_type)
        if color_fixed == color_type:
            raise ValueError('Unsupported color format: {}'.format(color_type))
        else:
            self.set_value(value, color_fixed)

    @multimethod(when="color_type=='hex'")
    def set_value(self, value, color_type):
        self.linear_rgb = self._rgb_from_hex(value)

    @multimethod(when="color_type=='linear_rgb'")
    def set_value(self, value, color_type):
        self.linear_rgb = value

    @multimethod(when="color_type=='rgb256'")
    def set_value(self, value, color_type):
        self.rgb = value

    @multimethod(when="color_type=='hls'")
    def set_value(self, value, color_type):
        self.hls = value

    @multimethod(when="color_type=='hsv'")
    def set_value(self, value, color_type):
        self.hsv = value

    @multimethod(when="color_type=='cmy'")
    def set_value(self, value, color_type):
        self.cmy = value

    @multimethod(when="color_type=='cmyk'")
    def set_value(self, value, color_type):
        self.cmyk = value

    # ChromaColor equality: difference is less than a tolerance
    # Use hex as the test for equals, as it is the greatest resolution without rounding issues
    def __eq__(self, other):
        return self.hex == other.hex if is_a(other, Color) else id(self) == id(other)

    def __ne__(self, other):
        return not (self == other)

    # Additive / subtractive mixing
    def __add__(self, other):
        return self.additive_mix(other)

    def __radd__(self, other):
        return other.additive_mix(self)

    def __sub__(self, other):
        return self.subtractive_mix(other)

    def __rsub__(self, other):
        return other.subtractive_mix(self)

    # Representation
    def __str__(self):
        return self.hex

    def __repr__(self):
        return self.__str__()

    #
    # Properties
    #

    # RGB
    # RGB is used as base, other formats will modify input into RGB and invoke
    # RGB getters / setters
    @property
    def linear_rgb(self):
        return self._append_alpha_if_necessary(self.color)

    @property
    def rgb(self):
        rgb256 = tuple(map(lambda x: int(round(x * 255)), self.color))
        return self._append_alpha_if_necessary(rgb256)

    @linear_rgb.setter
    def linear_rgb(self, color_tuple):
        """Used as main setter (rgb256, hls, hls256, hsv, hsv256)"""
        # Check bounds
        self.color = tuple(map(self._apply_float_bounds, color_tuple[:3]))

        # Include alpha if necessary
        if len(color_tuple) > 3:
            self.alpha = self._apply_float_bounds(color_tuple[3])

    @rgb.setter
    def rgb(self, color_tuple):
        self.linear_rgb = map(lambda x: x / 255.0, color_tuple)

    # HLS
    @property
    def hls(self):
        """
        HLS: (Hue°, Lightness%, Saturation%)
        Hue given as percent of 360, Lightness and Saturation given as percent
        """
        r, g, b = self.color
        hls = colorsys.rgb_to_hls(r, g, b)
        hls = (int(round(hls[0] * 360)), hls[1], hls[2])
        return self._append_alpha_if_necessary(hls)

    @hls.setter
    def hls(self, color_tuple):
        h, l, s = (self._apply_float_bounds(color_tuple[0] / 360.0),
                   self._apply_float_bounds(color_tuple[1]),
                   self._apply_float_bounds(color_tuple[2]))
        rgb = colorsys.hls_to_rgb(h, l, s)

        # Append alpha if included
        if len(color_tuple) > 3:
            rgb += (color_tuple[3],)

        self.linear_rgb = rgb

    # HSV
    @property
    def hsv(self):
        """
        HSV: (Hue°, Saturation%, Value%)
        Hue given as percent of 360, Saturation and Value given as percent
        """
        r, g, b = self.color
        hsv = colorsys.rgb_to_hsv(r, g, b)
        hsv = (int(round(hsv[0] * 360)), hsv[1], hsv[2])
        return self._append_alpha_if_necessary(hsv)

    @hsv.setter
    def hsv(self, color_tuple):
        h, s, v = (self._apply_float_bounds(color_tuple[0] / 360.0),
                   self._apply_float_bounds(color_tuple[1]),
                   self._apply_float_bounds(color_tuple[2]))
        rgb = colorsys.hsv_to_rgb(h, s, v)

        # Append alpha if included
        if len(color_tuple) > 3:
            rgb += (color_tuple[3],)

        self.linear_rgb = rgb

    # CMY / CMYK
    @property
    def cmy(self):
        """
        CMY: returned in range 0.0 - 1.0
        CMY is subtractive, e.g. black: (1, 1, 1), white (0, 0, 0)
        """
        r, g, b = self.color
        c = 1 - r
        m = 1 - g
        y = 1 - b

        return (c, m, y)

    @cmy.setter
    def cmy(self, color_tuple):
        c, m, y = tuple(map(lambda x: self._apply_float_bounds(x), color_tuple))[:3]
        r = 1 - c
        g = 1 - m
        b = 1 - y
        self.linear_rgb = (r, g, b)

    @property
    def cmyk(self):
        """CMYK: all returned in range 0.0 - 1.0"""
        c, m, y = self.cmy
        k = min(c, m, y)

        # Handle division by zero in case of black = 1
        if k != 1:
            c = (c - k) / (1 - k)
            m = (m - k) / (1 - k)
            y = (y - k) / (1 - k)
        else:
            c, m, y = 1, 1, 1

        cmyk = (c, m, y, k)

        # Apply bound and return
        return tuple(map(lambda x: self._apply_float_bounds(x), cmyk))

    @cmyk.setter
    def cmyk(self, color_tuple):
        c, m, y, k = tuple(map(lambda x: self._apply_float_bounds(x), color_tuple))[:4]
        c = c * (1 - k) + k
        m = m * (1 - k) + k
        y = y * (1 - k) + k
        self.cmy = (c, m, y)

    # HEX
    @property
    def hex(self):
        r = self._float_to_hex(self.color[0])
        g = self._float_to_hex(self.color[1])
        b = self._float_to_hex(self.color[2])
        rgb = '#' + r + g + b

        # Append alpha hex if necessary
        if self.alpha is not None:
            rgb += self._float_to_hex(self.alpha)

        return rgb

    @hex.setter
    def hex(self, color_value):
        self.linear_rgb = self._rgb_from_hex(color_value)

    # Alpha
    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        self._alpha = self._apply_float_bounds(value)

    #
    # ChromaColor Functions
    # Note: color functions return a ChromaColor object when called directly
    #

    # Additive (Light) Mixing
    def additive_mix(self, other):
        rgb_mix = tuple([rgb1 + rgb2 for rgb1, rgb2 in zip(self.linear_rgb, other.linear_rgb)])
        return Color(rgb_mix, 'RGB')

    # Subtractive (Dye, Multiplicative) Mixing
    def subtractive_mix(self, other):
        cmy_mix = tuple([cmy1 + cmy2 for cmy1, cmy2 in zip(self.cmy, other.cmy)])
        return Color(cmy_mix, 'CMY')

    #
    # INTERNAL
    #
    def _rgb_from_hex(self, color_value):
        hex_value = str(color_value)

        # Remove hash if exists
        if hex_value[0] == '#':
            hex_value = hex_value[1:]

        # Check length
        # 6: 6 digit hex
        # 8: 6 digit hex + alpha
        if len(hex_value) not in [6, 8]:
            raise ValueError('Invalid Hex Input: %s' % (color_value))

        # Return rgb from hex
        try:
            rgb = (int(hex_value[0:2], 16) / 255.0,
                   int(hex_value[2:4], 16) / 255.0,
                   int(hex_value[4:6], 16) / 255.0)

            # Append alpha if exists
            if len(hex_value) == 8:
                rgb += (int(hex_value[6:8], 16) / 255.0,)

            return rgb
        except Exception, e:
            raise ValueError('Invalid Hex Input: %s' % (color_value))

    @staticmethod
    def _float_to_hex(float_value):
        """
        Convert from float to in to hex number without 0x
        :param float_value:
        :return:
        """
        # Convert from float to in to hex number, remove '0x'
        int_value = int(round(float_value * 255))
        hex_value = hex(int_value)[2:]

        # If hex is only one digit, pad with 0
        if len(hex_value) == 1:
            hex_value = '0' + hex_value

        return hex_value.upper()

    @staticmethod
    def _apply_float_bounds(coordinate):
        """
        Assure coordinate is a float between 0 to 1
        :param coordinate:
        :return:
        """
        # Skip None for Alpha
        if coordinate == None:
            return None

        if coordinate < 0.0:
            return 0.0
        elif coordinate > 1.0:
            return 1.0

        return float(coordinate)

    def _append_alpha_if_necessary(self, color_tuple):
        """
        Return color_tuple with alpha if self.alpha is not None
        :param color_tuple:
        :return:
        """
        if self.alpha is not None:
            return color_tuple + (self.alpha,)
        return color_tuple

    def lighter(self, amount=0.2):
        """
        Return a lighter version of this color.
        :param amount: proportion between 0 and 1
        :return:
        """
        l = min(self.hls[1] + amount, 1.0)
        return Color(color_value=(self.hls[0], l, self.hls[2], self.alpha), color_type="hls")

    def darker(self, amount=0.2):
        """
        Return a lighter version of this color.
        :param amount: proportion between 0 and 1
        :return:
        """
        "Return a darker version of this color."
        l = max(self.hls[1] - amount, 0.0)
        return Color(color_value=(self.hls[0], l, self.hls[2], self.alpha), color_type="hls")

    def percentage(self, amount=1):
        """
        Return a color that represent a percentage of the color using TeX's algorithm.
        :param amount:
        :return:
        """
        rgb, alpha = self.linear_rgb[:3], self.alpha
        rgb_modified = [(1 - amount) + amount * v for v in rgb] + [alpha]
        return Color(color_value=rgb_modified, color_type="linear-rgb")

    def modify(self, modifier, value):
        modifier = modifier.lower()
        modifier = self._modifiers_convert.get(modifier, modifier)
        self.modifiers[modifier] = value

    def apply_modifiers(self):
        target = self
        for modifier, value in self.modifiers.items():
            target = self._apply_modifier(modifier, value, target=target)
        return target

    @multimethod()
    def _apply_modifier(self, modifier, value, target):
        raise ValueError('Unsupported modifier: {}'.format(modifier))

    @multimethod(when="modifier=='alpha'")
    def _apply_modifier(self, modifier, value, target):
        target.alpha = value
        return target

    @multimethod(when="modifier=='darker'")
    def _apply_modifier(self, modifier, value, target):
        return target.darker(value)

    @multimethod(when="modifier=='lighter'")
    def _apply_modifier(self, modifier, value, target):
        return target.lighter(value)

    @multimethod(when="modifier=='proportion'")
    def _apply_modifier(self, modifier, value, target):
        return target.percentage(float(value))

    def named_color(self, name):
        name = Color.format_color(name)
        self.rgb = Color.named_colors[name].rgb

    @staticmethod
    def format_color(name):
        return "".join(c for c in name.lower() if c.isalnum())

    @staticmethod
    def fill_named_colors():
        named = Color.format_color
        colors = Color.named_colors
        colors[named("Air Force blue")] = Color("#5D8AA8", 'hex')
        colors[named("Alice blue")] = Color("#F0F8FF", 'hex')
        colors[named("Alizarin")] = Color("#E32636", 'hex')
        colors[named("Almond")] = Color("#EFDECD", 'hex')
        colors[named("Amaranth")] = Color("#E52B50", 'hex')
        colors[named("Amber")] = Color("#FFBF00", 'hex')
        colors[named("Amber (SAE/ECE)")] = Color("#FF7E00", 'hex')
        colors[named("American rose")] = Color("#FF033E", 'hex')
        colors[named("Amethyst")] = Color("#9966CC", 'hex')
        colors[named("Anti-flash white")] = Color("#F2F3F4", 'hex')
        colors[named("Antique brass")] = Color("#CD9575", 'hex')
        colors[named("Antique fuchsia")] = Color("#915C83", 'hex')
        colors[named("Antique white")] = Color("#FAEBD7", 'hex')
        colors[named("Ao")] = Color("#0000FF", 'hex')
        colors[named("Ao (English)")] = Color("#008000", 'hex')
        colors[named("Apple green")] = Color("#8DB600", 'hex')
        colors[named("Apricot")] = Color("#FBCEB1", 'hex')
        colors[named("Aqua")] = Color("#00FFFF", 'hex')
        colors[named("Aquamarine")] = Color("#7FFFD0", 'hex')
        colors[named("Army green")] = Color("#4B5320", 'hex')
        colors[named("Arsenic")] = Color("#3B444B", 'hex')
        colors[named("Arylide yellow")] = Color("#E9D66B", 'hex')
        colors[named("Ash grey")] = Color("#B2BEB5", 'hex')
        colors[named("Asparagus")] = Color("#87A96B", 'hex')
        colors[named("Atomic tangerine")] = Color("#FF9966", 'hex')
        colors[named("Auburn")] = Color("#6D351A", 'hex')
        colors[named("Aureolin")] = Color("#FDEE00", 'hex')
        colors[named("AuroMetalSaurus")] = Color("#6E7F80", 'hex')
        colors[named("Awesome")] = Color("#FF2052", 'hex')
        colors[named("Azure (color wheel)")] = Color("#007FFF", 'hex')
        colors[named("Azure (web) (Azure mist)")] = Color("#F0FFFF", 'hex')
        colors[named("Baby blue")] = Color("#89CFF0", 'hex')
        colors[named("Baby blue eyes")] = Color("#A1CAF1", 'hex')
        colors[named("Baby pink")] = Color("#F4C2C2", 'hex')
        colors[named("Ball Blue")] = Color("#21ABCD", 'hex')
        colors[named("Banana Mania")] = Color("#FAE7B5", 'hex')
        colors[named("banana yellow")] = Color("#FFE135", 'hex')
        colors[named("Battleship grey")] = Color("#848482", 'hex')
        colors[named("Bazaar")] = Color("#98777B", 'hex')
        colors[named("Beau blue")] = Color("#BCD4E6", 'hex')
        colors[named("Beaver")] = Color("#9F8170", 'hex')
        colors[named("Beige")] = Color("#F5F5DC", 'hex')
        colors[named("Bisque")] = Color("#FFE4C4", 'hex')
        colors[named("Bistre")] = Color("#3D2B1F", 'hex')
        colors[named("Bittersweet")] = Color("#FE6F5E", 'hex')
        colors[named("Black")] = Color("#000000", 'hex')
        colors[named("Blanched Almond")] = Color("#FFEBCD", 'hex')
        colors[named("Bleu de France")] = Color("#318CE7", 'hex')
        colors[named("Blizzard Blue")] = Color("#ACE5EE", 'hex')
        colors[named("Blond")] = Color("#FAF0BE", 'hex')
        colors[named("Blue")] = Color("#0000FF", 'hex')
        colors[named("Blue (Munsell)")] = Color("#0093AF", 'hex')
        colors[named("Blue (NCS)")] = Color("#0087BD", 'hex')
        colors[named("Blue (pigment)")] = Color("#333399", 'hex')
        colors[named("Blue (RYB)")] = Color("#0247FE", 'hex')
        colors[named("Blue Bell")] = Color("#A2A2D0", 'hex')
        colors[named("Blue Gray")] = Color("#6699CC", 'hex')
        colors[named("Blue-green")] = Color("#00DDDD", 'hex')
        colors[named("Blue-violet")] = Color("#8A2BE2", 'hex')
        colors[named("Blush")] = Color("#DE5D83", 'hex')
        colors[named("Bole")] = Color("#79443B", 'hex')
        colors[named("Bondi blue")] = Color("#0095B6", 'hex')
        colors[named("Boston University Red")] = Color("#CC0000", 'hex')
        colors[named("Brandeis blue")] = Color("#0070FF", 'hex')
        colors[named("Brass")] = Color("#B5A642", 'hex')
        colors[named("Brick red")] = Color("#CB4154", 'hex')
        colors[named("Bright cerulean")] = Color("#1DACD6", 'hex')
        colors[named("Bright green")] = Color("#66FF00", 'hex')
        colors[named("Bright lavender")] = Color("#BF94E4", 'hex')
        colors[named("Bright maroon")] = Color("#C32148", 'hex')
        colors[named("Bright pink")] = Color("#FF007F", 'hex')
        colors[named("Bright turquoise")] = Color("#08E8DE", 'hex')
        colors[named("Bright ube")] = Color("#D19FE8", 'hex')
        colors[named("Brilliant lavender")] = Color("#F4BBFF", 'hex')
        colors[named("Brilliant rose")] = Color("#FF55A3", 'hex')
        colors[named("Brink pink")] = Color("#FB607F", 'hex')
        colors[named("British racing green")] = Color("#004225", 'hex')
        colors[named("Bronze")] = Color("#CD7F32", 'hex')
        colors[named("Brown (traditional)")] = Color("#964B00", 'hex')
        colors[named("Brown (web)")] = Color("#A52A2A", 'hex')
        colors[named("Bubble gum")] = Color("#FFC1CC", 'hex')
        colors[named("Bubbles")] = Color("#E7FEFF", 'hex')
        colors[named("Buff")] = Color("#F0DC82", 'hex')
        colors[named("Bulgarian rose")] = Color("#480607", 'hex')
        colors[named("Burgundy")] = Color("#800020", 'hex')
        colors[named("Burlywood")] = Color("#DEB887", 'hex')
        colors[named("Burnt orange")] = Color("#CC5500", 'hex')
        colors[named("Burnt sienna")] = Color("#E97451", 'hex')
        colors[named("Burnt umber")] = Color("#8A3324", 'hex')
        colors[named("Byzantine")] = Color("#BD33A4", 'hex')
        colors[named("Byzantium")] = Color("#702963", 'hex')
        colors[named("Cadet")] = Color("#536872", 'hex')
        colors[named("Cadet blue")] = Color("#5F9EA0", 'hex')
        colors[named("Cadet grey")] = Color("#91A3B0", 'hex')
        colors[named("Cadmium Green")] = Color("#006B3C", 'hex')
        colors[named("Cadmium Orange")] = Color("#ED872D", 'hex')
        colors[named("Cadmium Red")] = Color("#E30022", 'hex')
        colors[named("Cadmium Yellow")] = Color("#FFF600", 'hex')
        colors[named("Cal Poly Pomona green")] = Color("#1E4D2B", 'hex')
        colors[named("Cambridge Blue")] = Color("#A3C1AD", 'hex')
        colors[named("Camel")] = Color("#C19A6B", 'hex')
        colors[named("Camouflage green")] = Color("#78866B", 'hex')
        colors[named("Canary yellow")] = Color("#FFEF00", 'hex')
        colors[named("Candy apple red")] = Color("#FF0800", 'hex')
        colors[named("Candy pink")] = Color("#E4717A", 'hex')
        colors[named("Capri")] = Color("#00BFFF", 'hex')
        colors[named("Caput mortuum")] = Color("#592720", 'hex')
        colors[named("Cardinal")] = Color("#C41E3A", 'hex')
        colors[named("Caribbean green")] = Color("#00CC99", 'hex')
        colors[named("Carmine")] = Color("#960018", 'hex')
        colors[named("Carmine pink")] = Color("#EB4C42", 'hex')
        colors[named("Carmine red")] = Color("#FF0038", 'hex')
        colors[named("Carnation pink")] = Color("#FFA6C9", 'hex')
        colors[named("Carnelian")] = Color("#B31B1B", 'hex')
        colors[named("Carolina blue")] = Color("#99BADD", 'hex')
        colors[named("Carrot orange")] = Color("#ED9121", 'hex')
        colors[named("Ceil")] = Color("#92A1CF", 'hex')
        colors[named("Celadon")] = Color("#ACE1AF", 'hex')
        colors[named("Celestial blue")] = Color("#4997D0", 'hex')
        colors[named("Cerise")] = Color("#DE3163", 'hex')
        colors[named("Cerise pink")] = Color("#EC3B83", 'hex')
        colors[named("Cerulean")] = Color("#007BA7", 'hex')
        colors[named("Cerulean blue")] = Color("#2A52BE", 'hex')
        colors[named("Chamoisee")] = Color("#A0785A", 'hex')
        colors[named("Champagne")] = Color("#F7E7CE", 'hex')
        colors[named("Charcoal")] = Color("#36454F", 'hex')
        colors[named("Chartreuse (traditional)")] = Color("#DFFF00", 'hex')
        colors[named("Chartreuse (web)")] = Color("#7FFF00", 'hex')
        colors[named("Cherry blossom pink")] = Color("#FFB7C5", 'hex')
        colors[named("Chestnut")] = Color("#CD5C5C", 'hex')
        colors[named("Chocolate (traditional)")] = Color("#7B3F00", 'hex')
        colors[named("Chocolate (web)")] = Color("#D2691E", 'hex')
        colors[named("Chrome yellow")] = Color("#FFA700", 'hex')
        colors[named("Cinereous")] = Color("#98817B", 'hex')
        colors[named("Cinnabar")] = Color("#E34234", 'hex')
        colors[named("Cinnamon")] = Color("#D2691E", 'hex')
        colors[named("Citrine")] = Color("#E4D00A", 'hex')
        colors[named("Classic rose")] = Color("#FBCCE7", 'hex')
        colors[named("Cobalt")] = Color("#0047AB", 'hex')
        colors[named("Cocoa brown")] = Color("#D2691E", 'hex')
        colors[named("Columbia blue")] = Color("#9BDDFF", 'hex')
        colors[named("Cool black")] = Color("#002E63", 'hex')
        colors[named("Cool grey")] = Color("#8C92AC", 'hex')
        colors[named("Copper")] = Color("#B87333", 'hex')
        colors[named("Copper rose")] = Color("#996666", 'hex')
        colors[named("Coquelicot")] = Color("#FF3800", 'hex')
        colors[named("Coral")] = Color("#FF7F50", 'hex')
        colors[named("Coral pink")] = Color("#F88379", 'hex')
        colors[named("Coral red")] = Color("#FF4040", 'hex')
        colors[named("Cordovan")] = Color("#893F45", 'hex')
        colors[named("Corn")] = Color("#FBEC5D", 'hex')
        colors[named("Cornell Red")] = Color("#B31B1B", 'hex')
        colors[named("Cornflower blue")] = Color("#6495ED", 'hex')
        colors[named("Cornsilk")] = Color("#FFF8DC", 'hex')
        colors[named("Cosmic latte")] = Color("#FFF8E7", 'hex')
        colors[named("Cotton candy")] = Color("#FFBCD9", 'hex')
        colors[named("Cream")] = Color("#FFFDD0", 'hex')
        colors[named("Crimson")] = Color("#DC143C", 'hex')
        colors[named("Crimson glory")] = Color("#BE0032", 'hex')
        colors[named("Cyan")] = Color("#00FFFF", 'hex')
        colors[named("Cyan (process)")] = Color("#00B7EB", 'hex')
        colors[named("Daffodil")] = Color("#FFFF31", 'hex')
        colors[named("Dandelion")] = Color("#F0E130", 'hex')
        colors[named("Dark blue")] = Color("#00008B", 'hex')
        colors[named("Dark brown")] = Color("#654321", 'hex')
        colors[named("Dark byzantium")] = Color("#5D3954", 'hex')
        colors[named("Dark candy apple red")] = Color("#A40000", 'hex')
        colors[named("Dark cerulean")] = Color("#08457E", 'hex')
        colors[named("Dark champagne")] = Color("#C2B280", 'hex')
        colors[named("Dark chestnut")] = Color("#986960", 'hex')
        colors[named("Dark coral")] = Color("#CD5B45", 'hex')
        colors[named("Dark cyan")] = Color("#008B8B", 'hex')
        colors[named("Dark electric blue")] = Color("#536878", 'hex')
        colors[named("Dark goldenrod")] = Color("#B8860B", 'hex')
        colors[named("Dark gray")] = Color("#A9A9A9", 'hex')
        colors[named("Dark green")] = Color("#013220", 'hex')
        colors[named("Dark jungle green")] = Color("#1A2421", 'hex')
        colors[named("Dark khaki")] = Color("#BDB76B", 'hex')
        colors[named("Dark lava")] = Color("#483C32", 'hex')
        colors[named("Dark lavender")] = Color("#734F96", 'hex')
        colors[named("Dark magenta")] = Color("#8B008B", 'hex')
        colors[named("Dark midnight blue")] = Color("#003366", 'hex')
        colors[named("Dark olive green")] = Color("#556B2F", 'hex')
        colors[named("Dark orange")] = Color("#FF8C00", 'hex')
        colors[named("Dark orchid")] = Color("#9932CC", 'hex')
        colors[named("Dark pastel blue")] = Color("#779ECB", 'hex')
        colors[named("Dark pastel green")] = Color("#03C03C", 'hex')
        colors[named("Dark pastel purple")] = Color("#966FD6", 'hex')
        colors[named("Dark pastel red")] = Color("#C23B22", 'hex')
        colors[named("Dark pink")] = Color("#E75480", 'hex')
        colors[named("Dark powder blue")] = Color("#003399", 'hex')
        colors[named("Dark raspberry")] = Color("#872657", 'hex')
        colors[named("Dark red")] = Color("#8B0000", 'hex')
        colors[named("Dark salmon")] = Color("#E9967A", 'hex')
        colors[named("Dark scarlet")] = Color("#560319", 'hex')
        colors[named("Dark sea green")] = Color("#8FBC8F", 'hex')
        colors[named("Dark sienna")] = Color("#3C1414", 'hex')
        colors[named("Dark slate blue")] = Color("#483D8B", 'hex')
        colors[named("Dark slate gray")] = Color("#2F4F4F", 'hex')
        colors[named("Dark spring green")] = Color("#177245", 'hex')
        colors[named("Dark tan")] = Color("#918151", 'hex')
        colors[named("Dark tangerine")] = Color("#FFA812", 'hex')
        colors[named("Dark taupe")] = Color("#483C32", 'hex')
        colors[named("Dark terra cotta")] = Color("#CC4E5C", 'hex')
        colors[named("Dark turquoise")] = Color("#00CED1", 'hex')
        colors[named("Dark violet")] = Color("#9400D3", 'hex')
        colors[named("Dartmouth green")] = Color("#00693E", 'hex')
        colors[named("Davy\'s grey")] = Color("#555555", 'hex')
        colors[named("Debian red")] = Color("#D70A53", 'hex')
        colors[named("Deep carmine")] = Color("#A9203E", 'hex')
        colors[named("Deep carmine pink")] = Color("#EF3038", 'hex')
        colors[named("Deep carrot orange")] = Color("#E9692C", 'hex')
        colors[named("Deep cerise")] = Color("#DA3287", 'hex')
        colors[named("Deep champagne")] = Color("#FAD6A5", 'hex')
        colors[named("Deep chestnut")] = Color("#B94E48", 'hex')
        colors[named("Deep fuchsia")] = Color("#C154C1", 'hex')
        colors[named("Deep jungle green")] = Color("#004B49", 'hex')
        colors[named("Deep lilac")] = Color("#9955BB", 'hex')
        colors[named("Deep magenta")] = Color("#CC00CC", 'hex')
        colors[named("Deep peach")] = Color("#FFCBA4", 'hex')
        colors[named("Deep pink")] = Color("#FF1493", 'hex')
        colors[named("Deep saffron")] = Color("#FF9933", 'hex')
        colors[named("Deep sky blue")] = Color("#00BFFF", 'hex')
        colors[named("Denim")] = Color("#1560BD", 'hex')
        colors[named("Desert")] = Color("#C19A6B", 'hex')
        colors[named("Desert sand")] = Color("#EDC9AF", 'hex')
        colors[named("Dim gray")] = Color("#696969", 'hex')
        colors[named("Dodger blue")] = Color("#1E90FF", 'hex')
        colors[named("Dogwood rose")] = Color("#D71868", 'hex')
        colors[named("Dollar bill")] = Color("#85BB65", 'hex')
        colors[named("Drab")] = Color("#967117", 'hex')
        colors[named("Duke blue")] = Color("#00009C", 'hex')
        colors[named("Earth yellow")] = Color("#E1A95F", 'hex')
        colors[named("Ecru")] = Color("#C2B280", 'hex')
        colors[named("Eggplant")] = Color("#614051", 'hex')
        colors[named("Eggshell")] = Color("#F0EAD6", 'hex')
        colors[named("Egyptian blue")] = Color("#1034A6", 'hex')
        colors[named("Electric blue")] = Color("#7DF9FF", 'hex')
        colors[named("Electric crimson")] = Color("#FF003F", 'hex')
        colors[named("Electric cyan")] = Color("#00FFFF", 'hex')
        colors[named("Electric green")] = Color("#00FF00", 'hex')
        colors[named("Electric indigo")] = Color("#6F00FF", 'hex')
        colors[named("Electric lavender")] = Color("#F4BBFF", 'hex')
        colors[named("Electric lime")] = Color("#CCFF00", 'hex')
        colors[named("Electric purple")] = Color("#BF00FF", 'hex')
        colors[named("Electric ultramarine")] = Color("#3F00FF", 'hex')
        colors[named("Electric violet")] = Color("#8F00FF", 'hex')
        colors[named("Electric Yellow")] = Color("#FFFF00", 'hex')
        colors[named("Emerald")] = Color("#50C878", 'hex')
        colors[named("Eton blue")] = Color("#96C8A2", 'hex')
        colors[named("Fallow")] = Color("#C19A6B", 'hex')
        colors[named("Falu red")] = Color("#801818", 'hex')
        colors[named("Fandango")] = Color("#B53389", 'hex')
        colors[named("Fashion fuchsia")] = Color("#F400A1", 'hex')
        colors[named("Fawn")] = Color("#E5AA70", 'hex')
        colors[named("Feldgrau")] = Color("#4D5D53", 'hex')
        colors[named("Fern green")] = Color("#4F7942", 'hex')
        colors[named("Ferrari Red")] = Color("#FF2800", 'hex')
        colors[named("Field drab")] = Color("#6C541E", 'hex')
        colors[named("Firebrick")] = Color("#B22222", 'hex')
        colors[named("Fire engine red")] = Color("#CE2029", 'hex')
        colors[named("Flame")] = Color("#E25822", 'hex')
        colors[named("Flamingo pink")] = Color("#FC8EAC", 'hex')
        colors[named("Flavescent")] = Color("#F7E98E", 'hex')
        colors[named("Flax")] = Color("#EEDC82", 'hex')
        colors[named("Floral white")] = Color("#FFFAF0", 'hex')
        colors[named("Fluorescent orange")] = Color("#FFBF00", 'hex')
        colors[named("Fluorescent pink")] = Color("#FF1493", 'hex')
        colors[named("Fluorescent yellow")] = Color("#CCFF00", 'hex')
        colors[named("Folly")] = Color("#FF004F", 'hex')
        colors[named("Forest green (traditional)")] = Color("#014421", 'hex')
        colors[named("Forest green (web)")] = Color("#228B22", 'hex')
        colors[named("French beige")] = Color("#A67B5B", 'hex')
        colors[named("French blue")] = Color("#0072BB", 'hex')
        colors[named("French lilac")] = Color("#86608E", 'hex')
        colors[named("French rose")] = Color("#F64A8A", 'hex')
        colors[named("Fuchsia")] = Color("#FF00FF", 'hex')
        colors[named("Fuchsia pink")] = Color("#FF77FF", 'hex')
        colors[named("Fulvous")] = Color("#E48400", 'hex')
        colors[named("Fuzzy Wuzzy")] = Color("#CC6666", 'hex')
        colors[named("Gainsboro")] = Color("#DCDCDC", 'hex')
        colors[named("Gamboge")] = Color("#E49B0F", 'hex')
        colors[named("Ghost white")] = Color("#F8F8FF", 'hex')
        colors[named("Ginger")] = Color("#B06500", 'hex')
        colors[named("Glaucous")] = Color("#6082B6", 'hex')
        colors[named("Gold (metallic)")] = Color("#D4AF37", 'hex')
        colors[named("Gold (web) (Golden)")] = Color("#FFD700", 'hex')
        colors[named("Golden brown")] = Color("#996515", 'hex')
        colors[named("Golden poppy")] = Color("#FCC200", 'hex')
        colors[named("Golden yellow")] = Color("#FFDF00", 'hex')
        colors[named("Goldenrod")] = Color("#DAA520", 'hex')
        colors[named("Granny Smith Apple")] = Color("#A8E4A0", 'hex')
        colors[named("Gray")] = Color("#808080", 'hex')
        colors[named("Gray (HTML/CSS gray)")] = Color("#7F7F7F", 'hex')
        colors[named("Gray (X11 gray)")] = Color("#BEBEBE", 'hex')
        colors[named("Gray-asparagus")] = Color("#465945", 'hex')
        colors[named("Green (color wheel) (X11 green)")] = Color("#00FF00", 'hex')
        colors[named("Green (HTML/CSS green)")] = Color("#008000", 'hex')
        colors[named("Green (Munsell)")] = Color("#00A877", 'hex')
        colors[named("Green (NCS)")] = Color("#009F6B", 'hex')
        colors[named("Green (pigment)")] = Color("#00A550", 'hex')
        colors[named("Green (RYB)")] = Color("#66B032", 'hex')
        colors[named("Green-yellow")] = Color("#ADFF2F", 'hex')
        colors[named("Grullo")] = Color("#A99A86", 'hex')
        colors[named("Guppie green")] = Color("#00FF7F", 'hex')
        colors[named("Halaya ube")] = Color("#663854", 'hex')
        colors[named("Han blue")] = Color("#446CCF", 'hex')
        colors[named("Han purple")] = Color("#5218FA", 'hex')
        colors[named("Hansa yellow")] = Color("#E9D66B", 'hex')
        colors[named("Harlequin")] = Color("#3FFF00", 'hex')
        colors[named("Harvard crimson")] = Color("#C90016", 'hex')
        colors[named("Harvest Gold")] = Color("#DA9100", 'hex')
        colors[named("Heart Gold")] = Color("#808000", 'hex')
        colors[named("Heliotrope")] = Color("#DF73FF", 'hex')
        colors[named("Hollywood cerise")] = Color("#F400A1", 'hex')
        colors[named("Honeydew")] = Color("#F0FFF0", 'hex')
        colors[named("Hooker\'s green")] = Color("#007000", 'hex')
        colors[named("Hot magenta")] = Color("#FF1DCE", 'hex')
        colors[named("Hot pink")] = Color("#FF69B4", 'hex')
        colors[named("Hunter green")] = Color("#355E3B", 'hex')
        colors[named("Iceberg")] = Color("#71A6D2", 'hex')
        colors[named("Icterine")] = Color("#FCF75E", 'hex')
        colors[named("Inchworm")] = Color("#B2EC5D", 'hex')
        colors[named("India green")] = Color("#138808", 'hex')
        colors[named("Indian red")] = Color("#CD5C5C", 'hex')
        colors[named("Indian yellow")] = Color("#E3A857", 'hex')
        colors[named("Indigo (dye)")] = Color("#00416A", 'hex')
        colors[named("Indigo (web)")] = Color("#4B0082", 'hex')
        colors[named("International Klein Blue")] = Color("#002FA7", 'hex')
        colors[named("International orange")] = Color("#FF4F00", 'hex')
        colors[named("Iris")] = Color("#5A4FCF", 'hex')
        colors[named("Isabelline")] = Color("#F4F0EC", 'hex')
        colors[named("Islamic green")] = Color("#009000", 'hex')
        colors[named("Ivory")] = Color("#FFFFF0", 'hex')
        colors[named("Jade")] = Color("#00A86B", 'hex')
        colors[named("Jasper")] = Color("#D73B3E", 'hex')
        colors[named("Jazzberry jam")] = Color("#A50B5E", 'hex')
        colors[named("Jonquil")] = Color("#FADA5E", 'hex')
        colors[named("June bud")] = Color("#BDDA57", 'hex')
        colors[named("Jungle green")] = Color("#29AB87", 'hex')
        colors[named("Kelly green")] = Color("#4CBB17", 'hex')
        colors[named("Khaki (HTML/CSS) (Khaki)")] = Color("#C3B091", 'hex')
        colors[named("Khaki (X11) (Light khaki)")] = Color("#F0E68C", 'hex')
        colors[named("La Salle Green")] = Color("#087830", 'hex')
        colors[named("Languid lavender")] = Color("#D6CADD", 'hex')
        colors[named("Lapis lazuli")] = Color("#26619C", 'hex')
        colors[named("Laser Lemon")] = Color("#FEFE22", 'hex')
        colors[named("Lava")] = Color("#CF1020", 'hex')
        colors[named("Lavender (floral)")] = Color("#B57EDC", 'hex')
        colors[named("Lavender (web)")] = Color("#E6E6FA", 'hex')
        colors[named("Lavender blue")] = Color("#CCCCFF", 'hex')
        colors[named("Lavender blush")] = Color("#FFF0F5", 'hex')
        colors[named("Lavender gray")] = Color("#C4C3D0", 'hex')
        colors[named("Lavender indigo")] = Color("#9457EB", 'hex')
        colors[named("Lavender magenta")] = Color("#EE82EE", 'hex')
        colors[named("Lavender mist")] = Color("#E6E6FA", 'hex')
        colors[named("Lavender pink")] = Color("#FBAED2", 'hex')
        colors[named("Lavender purple")] = Color("#967BB6", 'hex')
        colors[named("Lavender rose")] = Color("#FBA0E3", 'hex')
        colors[named("Lawn green")] = Color("#7CFC00", 'hex')
        colors[named("Lemon")] = Color("#FFF700", 'hex')
        colors[named("Lemon chiffon")] = Color("#FFFACD", 'hex')
        colors[named("Light apricot")] = Color("#FDD5B1", 'hex')
        colors[named("Light blue")] = Color("#ADD8E6", 'hex')
        colors[named("Light brown")] = Color("#B5651D", 'hex')
        colors[named("Light carmine pink")] = Color("#E66771", 'hex')
        colors[named("Light coral")] = Color("#F08080", 'hex')
        colors[named("Light cornflower blue")] = Color("#93CCEA", 'hex')
        colors[named("Light cyan")] = Color("#E0FFFF", 'hex')
        colors[named("Light fuchsia pink")] = Color("#F984EF", 'hex')
        colors[named("Light goldenrod yellow")] = Color("#FAFAD2", 'hex')
        colors[named("Light gray")] = Color("#D3D3D3", 'hex')
        colors[named("Light green")] = Color("#90EE90", 'hex')
        colors[named("Light khaki")] = Color("#F0E68C", 'hex')
        colors[named("Light mauve")] = Color("#DCD0FF", 'hex')
        colors[named("Light pastel purple")] = Color("#B19CD9", 'hex')
        colors[named("Light pink")] = Color("#FFB6C1", 'hex')
        colors[named("Light salmon")] = Color("#FFA07A", 'hex')
        colors[named("Light salmon pink")] = Color("#FF9999", 'hex')
        colors[named("Light sea green")] = Color("#20B2AA", 'hex')
        colors[named("Light sky blue")] = Color("#87CEEB", 'hex')
        colors[named("Light slate gray")] = Color("#778899", 'hex')
        colors[named("Light taupe")] = Color("#B38B6D", 'hex')
        colors[named("Light Thulian pink")] = Color("#E68FAC", 'hex')
        colors[named("Light yellow")] = Color("#FFFFED", 'hex')
        colors[named("Lilac")] = Color("#C8A2C8", 'hex')
        colors[named("Lime (color wheel)")] = Color("#BFFF00", 'hex')
        colors[named("Lime (web) (X11 green)")] = Color("#00FF00", 'hex')
        colors[named("Lime green")] = Color("#32CD32", 'hex')
        colors[named("Lincoln green")] = Color("#195905", 'hex')
        colors[named("Linen")] = Color("#FAF0E6", 'hex')
        colors[named("Liver")] = Color("#534B4F", 'hex')
        colors[named("Lust")] = Color("#E62020", 'hex')
        colors[named("Macaroni and Cheese")] = Color("#FFBD88", 'hex')
        colors[named("Magenta")] = Color("#FF00FF", 'hex')
        colors[named("Magenta (dye)")] = Color("#CA1F7B", 'hex')
        colors[named("Magenta (process)")] = Color("#FF0090", 'hex')
        colors[named("Magic mint")] = Color("#AAF0D1", 'hex')
        colors[named("Magnolia")] = Color("#F8F4FF", 'hex')
        colors[named("Mahogany")] = Color("#C04000", 'hex')
        colors[named("Maize")] = Color("#FBEC5D", 'hex')
        colors[named("Majorelle Blue")] = Color("#6050DC", 'hex')
        colors[named("Malachite")] = Color("#0BDA51", 'hex')
        colors[named("Manatee")] = Color("#979AAA", 'hex')
        colors[named("Mango Tango")] = Color("#FF8243", 'hex')
        colors[named("Maroon (HTML/CSS)")] = Color("#800000", 'hex')
        colors[named("Maroon (X11)")] = Color("#B03060", 'hex')
        colors[named("Mauve")] = Color("#E0B0FF", 'hex')
        colors[named("Mauve taupe")] = Color("#915F6D", 'hex')
        colors[named("Mauvelous")] = Color("#EF98AA", 'hex')
        colors[named("Maya blue")] = Color("#73C2FB", 'hex')
        colors[named("Meat brown")] = Color("#E5B73B", 'hex')
        colors[named("Medium aquamarine")] = Color("#66DDAA", 'hex')
        colors[named("Medium blue")] = Color("#0000CD", 'hex')
        colors[named("Medium candy apple red")] = Color("#E2062C", 'hex')
        colors[named("Medium carmine")] = Color("#AF4035", 'hex')
        colors[named("Medium champagne")] = Color("#F3E5AB", 'hex')
        colors[named("Medium electric blue")] = Color("#035096", 'hex')
        colors[named("Medium jungle green")] = Color("#1C352D", 'hex')
        colors[named("Medium lavender magenta")] = Color("#DDA0DD", 'hex')
        colors[named("Medium orchid")] = Color("#BA55D3", 'hex')
        colors[named("Medium Persian blue")] = Color("#0067A5", 'hex')
        colors[named("Medium purple")] = Color("#9370DB", 'hex')
        colors[named("Medium red-violet")] = Color("#BB3385", 'hex')
        colors[named("Medium sea green")] = Color("#3CB371", 'hex')
        colors[named("Medium slate blue")] = Color("#7B68EE", 'hex')
        colors[named("Medium spring bud")] = Color("#C9DC87", 'hex')
        colors[named("Medium spring green")] = Color("#00FA9A", 'hex')
        colors[named("Medium taupe")] = Color("#674C47", 'hex')
        colors[named("Medium teal blue")] = Color("#0054B4", 'hex')
        colors[named("Medium turquoise")] = Color("#48D1CC", 'hex')
        colors[named("Medium violet-red")] = Color("#C71585", 'hex')
        colors[named("Melon")] = Color("#FDBCB4", 'hex')
        colors[named("Midnight blue")] = Color("#191970", 'hex')
        colors[named("Midnight green (eagle green)")] = Color("#004953", 'hex')
        colors[named("Mikado yellow")] = Color("#FFC40C", 'hex')
        colors[named("Mint")] = Color("#3EB489", 'hex')
        colors[named("Mint cream")] = Color("#F5FFFA", 'hex')
        colors[named("Mint green")] = Color("#98FF98", 'hex')
        colors[named("Misty rose")] = Color("#FFE4E1", 'hex')
        colors[named("Moccasin")] = Color("#FAEBD7", 'hex')
        colors[named("Mode beige")] = Color("#967117", 'hex')
        colors[named("Moonstone blue")] = Color("#73A9C2", 'hex')
        colors[named("Mordant red 19")] = Color("#AE0C00", 'hex')
        colors[named("Moss green")] = Color("#ADDFAD", 'hex')
        colors[named("Mountain Meadow")] = Color("#30BA8F", 'hex')
        colors[named("Mountbatten pink")] = Color("#997A8D", 'hex')
        colors[named("Mulberry")] = Color("#C54B8C", 'hex')
        colors[named("Mustard")] = Color("#FFDB58", 'hex')
        colors[named("Myrtle")] = Color("#21421E", 'hex')
        colors[named("MSU Green")] = Color("#18453B", 'hex')
        colors[named("Nadeshiko pink")] = Color("#F6ADC6", 'hex')
        colors[named("Napier green")] = Color("#2A8000", 'hex')
        colors[named("Naples yellow")] = Color("#FADA5E", 'hex')
        colors[named("Navajo white")] = Color("#FFDEAD", 'hex')
        colors[named("Navy blue")] = Color("#000080", 'hex')
        colors[named("Neon Carrot")] = Color("#FFA343", 'hex')
        colors[named("Neon fuchsia")] = Color("#FE59C2", 'hex')
        colors[named("Neon green")] = Color("#39FF14", 'hex')
        colors[named("Non-photo blue")] = Color("#A4DDED", 'hex')
        colors[named("Ocean Boat Blue")] = Color("#0077BE", 'hex')
        colors[named("Ochre")] = Color("#CC7722", 'hex')
        colors[named("Office green")] = Color("#008000", 'hex')
        colors[named("Old gold")] = Color("#CFB53B", 'hex')
        colors[named("Old lace")] = Color("#FDF5E6", 'hex')
        colors[named("Old lavender")] = Color("#796878", 'hex')
        colors[named("Old mauve")] = Color("#673147", 'hex')
        colors[named("Old rose")] = Color("#C08081", 'hex')
        colors[named("Olive")] = Color("#808000", 'hex')
        colors[named("Olive Drab (web) (Olive Drab")] = Color("#333333", 'hex')
        colors[named("Olive Drab")] = Color("#777777", 'hex')
        colors[named("Olivine")] = Color("#9AB973", 'hex')
        colors[named("Onyx")] = Color("#0F0F0F", 'hex')
        colors[named("Opera mauve")] = Color("#B784A7", 'hex')
        colors[named("Orange (color wheel)")] = Color("#FF7F00", 'hex')
        colors[named("Orange (RYB)")] = Color("#FB9902", 'hex')
        colors[named("Orange (web color)")] = Color("#FFA500", 'hex')
        colors[named("Orange peel")] = Color("#FF9F00", 'hex')
        colors[named("Orange-red")] = Color("#FF4500", 'hex')
        colors[named("Orchid")] = Color("#DA70D6", 'hex')
        colors[named("Otter brown")] = Color("#654321", 'hex')
        colors[named("Outer Space")] = Color("#414A4C", 'hex')
        colors[named("Outrageous Orange")] = Color("#FF6E4A", 'hex')
        colors[named("Oxford Blue")] = Color("#002147", 'hex')
        colors[named("OU Crimson Red")] = Color("#990000", 'hex')
        colors[named("Pakistan green")] = Color("#006600", 'hex')
        colors[named("Palatinate blue")] = Color("#273BE2", 'hex')
        colors[named("Palatinate purple")] = Color("#682860", 'hex')
        colors[named("Pale aqua")] = Color("#BCD4E6", 'hex')
        colors[named("Pale blue")] = Color("#AFEEEE", 'hex')
        colors[named("Pale brown")] = Color("#987654", 'hex')
        colors[named("Pale carmine")] = Color("#AF4035", 'hex')
        colors[named("Pale cerulean")] = Color("#9BC4E2", 'hex')
        colors[named("Pale chestnut")] = Color("#DDADAF", 'hex')
        colors[named("Pale copper")] = Color("#DA8A67", 'hex')
        colors[named("Pale cornflower blue")] = Color("#ABCDEF", 'hex')
        colors[named("Pale gold")] = Color("#E6BE8A", 'hex')
        colors[named("Pale goldenrod")] = Color("#EEE8AA", 'hex')
        colors[named("Pale green")] = Color("#98FB98", 'hex')
        colors[named("Pale magenta")] = Color("#F984E5", 'hex')
        colors[named("Pale pink")] = Color("#FADADD", 'hex')
        colors[named("Pale plum")] = Color("#DDA0DD", 'hex')
        colors[named("Pale red-violet")] = Color("#DB7093", 'hex')
        colors[named("Pale robin egg blue")] = Color("#96DED1", 'hex')
        colors[named("Pale silver")] = Color("#C9C0BB", 'hex')
        colors[named("Pale spring bud")] = Color("#ECEBBD", 'hex')
        colors[named("Pale taupe")] = Color("#BC987E", 'hex')
        colors[named("Pale violet-red")] = Color("#DB7093", 'hex')
        colors[named("Pansy purple")] = Color("#78184A", 'hex')
        colors[named("Papaya whip")] = Color("#FFEFD5", 'hex')
        colors[named("Paris Green")] = Color("#50C878", 'hex')
        colors[named("Pastel blue")] = Color("#AEC6CF", 'hex')
        colors[named("Pastel brown")] = Color("#836953", 'hex')
        colors[named("Pastel gray")] = Color("#CFCFC4", 'hex')
        colors[named("Pastel green")] = Color("#77DD77", 'hex')
        colors[named("Pastel magenta")] = Color("#F49AC2", 'hex')
        colors[named("Pastel orange")] = Color("#FFB347", 'hex')
        colors[named("Pastel pink")] = Color("#FFD1DC", 'hex')
        colors[named("Pastel purple")] = Color("#B39EB5", 'hex')
        colors[named("Pastel red")] = Color("#FF6961", 'hex')
        colors[named("Pastel violet")] = Color("#CB99C9", 'hex')
        colors[named("Pastel yellow")] = Color("#FDFD96", 'hex')
        colors[named("Patriarch")] = Color("#800080", 'hex')
        colors[named("Payne\'s grey")] = Color("#40404F", 'hex')
        colors[named("Peach")] = Color("#FFE5B4", 'hex')
        colors[named("Peach-orange")] = Color("#FFCC99", 'hex')
        colors[named("Peach puff")] = Color("#FFDAB9", 'hex')
        colors[named("Peach-yellow")] = Color("#FADFAD", 'hex')
        colors[named("Pear")] = Color("#D1E231", 'hex')
        colors[named("Pearl")] = Color("#F0EAD6", 'hex')
        colors[named("Peridot")] = Color("#E6E200", 'hex')
        colors[named("Periwinkle")] = Color("#CCCCFF", 'hex')
        colors[named("Persian blue")] = Color("#1C39BB", 'hex')
        colors[named("Persian green")] = Color("#00A693", 'hex')
        colors[named("Persian indigo")] = Color("#32127A", 'hex')
        colors[named("Persian orange")] = Color("#D99058", 'hex')
        colors[named("Peru")] = Color("#CD853F", 'hex')
        colors[named("Persian pink")] = Color("#F77FBE", 'hex')
        colors[named("Persian plum")] = Color("#701C1C", 'hex')
        colors[named("Persian red")] = Color("#CC3333", 'hex')
        colors[named("Persian rose")] = Color("#FE28A2", 'hex')
        colors[named("Persimmon")] = Color("#EC5800", 'hex')
        colors[named("Phlox")] = Color("#DF00FF", 'hex')
        colors[named("Phthalo blue")] = Color("#000F89", 'hex')
        colors[named("Phthalo green")] = Color("#123524", 'hex')
        colors[named("Piggy pink")] = Color("#FDDDE6", 'hex')
        colors[named("Pine green")] = Color("#01796F", 'hex')
        colors[named("Pink")] = Color("#FFC0CB", 'hex')
        colors[named("Pink-orange")] = Color("#FF9966", 'hex')
        colors[named("Pink pearl")] = Color("#E7ACCF", 'hex')
        colors[named("Pink Sherbet")] = Color("#F78FA7", 'hex')
        colors[named("Pistachio")] = Color("#93C572", 'hex')
        colors[named("Platinum")] = Color("#E5E4E2", 'hex')
        colors[named("Plum (traditional)")] = Color("#8E4585", 'hex')
        colors[named("Plum (web)")] = Color("#DDA0DD", 'hex')
        colors[named("Portland Orange")] = Color("#FF5A36", 'hex')
        colors[named("Powder blue (web)")] = Color("#B0E0E6", 'hex')
        colors[named("Princeton orange")] = Color("#FF8F00", 'hex')
        colors[named("Prune")] = Color("#701C1C", 'hex')
        colors[named("Prussian blue")] = Color("#003153", 'hex')
        colors[named("Psychedelic purple")] = Color("#DF00FF", 'hex')
        colors[named("Puce")] = Color("#CC8899", 'hex')
        colors[named("Pumpkin")] = Color("#FF7518", 'hex')
        colors[named("Purple (HTML/CSS)")] = Color("#800080", 'hex')
        colors[named("Purple (Munsell)")] = Color("#9F00C5", 'hex')
        colors[named("Purple (X11)")] = Color("#A020F0", 'hex')
        colors[named("Purple Heart")] = Color("#69359C", 'hex')
        colors[named("Purple mountain majesty")] = Color("#9678B6", 'hex')
        colors[named("Purple pizzazz")] = Color("#FE4EDA", 'hex')
        colors[named("Purple taupe")] = Color("#50404D", 'hex')
        colors[named("Radical Red")] = Color("#FF355E", 'hex')
        colors[named("Raspberry")] = Color("#E30B5D", 'hex')
        colors[named("Raspberry glace")] = Color("#915F6D", 'hex')
        colors[named("Raspberry pink")] = Color("#E25098", 'hex')
        colors[named("Raspberry rose")] = Color("#B3446C", 'hex')
        colors[named("Raw umber")] = Color("#826644", 'hex')
        colors[named("Razzle dazzle rose")] = Color("#FF33CC", 'hex')
        colors[named("Razzmatazz")] = Color("#E3256B", 'hex')
        colors[named("Red")] = Color("#FF0000", 'hex')
        colors[named("Red (Munsell)")] = Color("#F2003C", 'hex')
        colors[named("Red (NCS)")] = Color("#C40233", 'hex')
        colors[named("Red (pigment)")] = Color("#ED1C24", 'hex')
        colors[named("Red (RYB)")] = Color("#FE2712", 'hex')
        colors[named("Red-brown")] = Color("#A52A2A", 'hex')
        colors[named("Red-violet")] = Color("#C71585", 'hex')
        colors[named("Redwood")] = Color("#AB4E52", 'hex')
        colors[named("Regalia")] = Color("#522D80", 'hex')
        colors[named("Rich black")] = Color("#004040", 'hex')
        colors[named("Rich brilliant lavender")] = Color("#F1A7FE", 'hex')
        colors[named("Rich carmine")] = Color("#D70040", 'hex')
        colors[named("Rich electric blue")] = Color("#0892D0", 'hex')
        colors[named("Rich lavender")] = Color("#A76BCF", 'hex')
        colors[named("Rich lilac")] = Color("#B666D2", 'hex')
        colors[named("Rich maroon")] = Color("#B03060", 'hex')
        colors[named("Rifle green")] = Color("#414833", 'hex')
        colors[named("Robin egg blue")] = Color("#00CCCC", 'hex')
        colors[named("Rose")] = Color("#FF007F", 'hex')
        colors[named("Rose bonbon")] = Color("#F9429E", 'hex')
        colors[named("Rose ebony")] = Color("#674846", 'hex')
        colors[named("Rose gold")] = Color("#B76E79", 'hex')
        colors[named("Rose madder")] = Color("#E32636", 'hex')
        colors[named("Rose pink")] = Color("#FF66CC", 'hex')
        colors[named("Rose quartz")] = Color("#AA98A9", 'hex')
        colors[named("Rose taupe")] = Color("#905D5D", 'hex')
        colors[named("Rose vale")] = Color("#AB4E52", 'hex')
        colors[named("Rosewood")] = Color("#65000B", 'hex')
        colors[named("Rosso corsa")] = Color("#D40000", 'hex')
        colors[named("Rosy brown")] = Color("#BC8F8F", 'hex')
        colors[named("Royal azure")] = Color("#0038A8", 'hex')
        colors[named("Royal blue (traditional)")] = Color("#002366", 'hex')
        colors[named("Royal blue (web)")] = Color("#4169E1", 'hex')
        colors[named("Royal fuchsia")] = Color("#CA2C92", 'hex')
        colors[named("Royal purple")] = Color("#7851A9", 'hex')
        colors[named("Ruby")] = Color("#E0115F", 'hex')
        colors[named("Ruddy")] = Color("#FF0028", 'hex')
        colors[named("Ruddy brown")] = Color("#BB6528", 'hex')
        colors[named("Ruddy pink")] = Color("#E18E96", 'hex')
        colors[named("Rufous")] = Color("#A81C07", 'hex')
        colors[named("Russet")] = Color("#80461B", 'hex')
        colors[named("Rust")] = Color("#B7410E", 'hex')
        colors[named("Sacramento State green")] = Color("#00563F", 'hex')
        colors[named("Saddle brown")] = Color("#8B4513", 'hex')
        colors[named("Safety orange (blaze orange)")] = Color("#FF6700", 'hex')
        colors[named("Saffron")] = Color("#F4C430", 'hex')
        colors[named("St. Patrick\'s blue")] = Color("#23297A", 'hex')
        colors[named("Salmon")] = Color("#FF8C69", 'hex')
        colors[named("Salmon pink")] = Color("#FF91A4", 'hex')
        colors[named("Sand")] = Color("#C2B280", 'hex')
        colors[named("Sand dune")] = Color("#967117", 'hex')
        colors[named("Sandstorm")] = Color("#ECD540", 'hex')
        colors[named("Sandy brown")] = Color("#F4A460", 'hex')
        colors[named("Sandy taupe")] = Color("#967117", 'hex')
        colors[named("Sangria")] = Color("#92000A", 'hex')
        colors[named("Sap green")] = Color("#507D2A", 'hex')
        colors[named("Sapphire")] = Color("#082567", 'hex')
        colors[named("Satin sheen gold")] = Color("#CBA135", 'hex')
        colors[named("Scarlet")] = Color("#FF2000", 'hex')
        colors[named("School bus yellow")] = Color("#FFD800", 'hex')
        colors[named("Screamin\' Green")] = Color("#76FF7A", 'hex')
        colors[named("Sea green")] = Color("#2E8B57", 'hex')
        colors[named("Seal brown")] = Color("#321414", 'hex')
        colors[named("Seashell")] = Color("#FFF5EE", 'hex')
        colors[named("Selective yellow")] = Color("#FFBA00", 'hex')
        colors[named("Sepia")] = Color("#704214", 'hex')
        colors[named("Shadow")] = Color("#8A795D", 'hex')
        colors[named("Shamrock green")] = Color("#009E60", 'hex')
        colors[named("Shocking pink")] = Color("#FC0FC0", 'hex')
        colors[named("Sienna")] = Color("#882D17", 'hex')
        colors[named("Silver")] = Color("#C0C0C0", 'hex')
        colors[named("Sinopia")] = Color("#CB410B", 'hex')
        colors[named("Skobeloff")] = Color("#007474", 'hex')
        colors[named("Sky blue")] = Color("#87CEEB", 'hex')
        colors[named("Sky magenta")] = Color("#CF71AF", 'hex')
        colors[named("Slate blue")] = Color("#6A5ACD", 'hex')
        colors[named("Slate gray")] = Color("#708090", 'hex')
        colors[named("Smalt (Dark powder blue)")] = Color("#003399", 'hex')
        colors[named("Smokey topaz")] = Color("#933D41", 'hex')
        colors[named("Smoky black")] = Color("#100C08", 'hex')
        colors[named("Snow")] = Color("#FFFAFA", 'hex')
        colors[named("Spiro Disco Ball")] = Color("#0FC0FC", 'hex')
        colors[named("Splashed white")] = Color("#FEFDFF", 'hex')
        colors[named("Spring bud")] = Color("#A7FC00", 'hex')
        colors[named("Spring green")] = Color("#00FF7F", 'hex')
        colors[named("Steel blue")] = Color("#4682B4", 'hex')
        colors[named("Stil de grain yellow")] = Color("#FADA5E", 'hex')
        colors[named("Straw")] = Color("#E4D96F", 'hex')
        colors[named("Sunglow")] = Color("#FFCC33", 'hex')
        colors[named("Sunset")] = Color("#FAD6A5", 'hex')
        colors[named("Tan")] = Color("#D2B48C", 'hex')
        colors[named("Tangelo")] = Color("#F94D00", 'hex')
        colors[named("Tangerine")] = Color("#F28500", 'hex')
        colors[named("Tangerine yellow")] = Color("#FFCC00", 'hex')
        colors[named("Taupe")] = Color("#483C32", 'hex')
        colors[named("Taupe gray")] = Color("#8B8589", 'hex')
        colors[named("Tea green")] = Color("#D0F0C0", 'hex')
        colors[named("Tea rose (orange)")] = Color("#F88379", 'hex')
        colors[named("Tea rose (rose)")] = Color("#F4C2C2", 'hex')
        colors[named("Teal")] = Color("#008080", 'hex')
        colors[named("Teal blue")] = Color("#367588", 'hex')
        colors[named("Teal green")] = Color("#006D5B", 'hex')
        colors[named("Tenné (Tawny)")] = Color("#CD5700", 'hex')
        colors[named("Terra cotta")] = Color("#E2725B", 'hex')
        colors[named("Thistle")] = Color("#D8BFD8", 'hex')
        colors[named("Thulian pink")] = Color("#DE6FA1", 'hex')
        colors[named("Tickle Me Pink")] = Color("#FC89AC", 'hex')
        colors[named("Tiffany Blue")] = Color("#0ABAB5", 'hex')
        colors[named("Tiger\'s eye")] = Color("#E08D3C", 'hex')
        colors[named("Timberwolf")] = Color("#DBD7D2", 'hex')
        colors[named("Titanium yellow")] = Color("#EEE600", 'hex')
        colors[named("Tomato")] = Color("#FF6347", 'hex')
        colors[named("Toolbox")] = Color("#746CC0", 'hex')
        colors[named("Tractor red")] = Color("#FD0E35", 'hex')
        colors[named("Trolley Grey")] = Color("#808080", 'hex')
        colors[named("Tropical rain forest")] = Color("#00755E", 'hex')
        colors[named("True Blue")] = Color("#0073CF", 'hex')
        colors[named("Tufts Blue")] = Color("#417DC1", 'hex')
        colors[named("Tumbleweed")] = Color("#DEAA88", 'hex')
        colors[named("Turkish rose")] = Color("#B57281", 'hex')
        colors[named("Turquoise")] = Color("#30D5C8", 'hex')
        colors[named("Turquoise blue")] = Color("#00FFEF", 'hex')
        colors[named("Turquoise green")] = Color("#A0D6B4", 'hex')
        colors[named("Tuscan red")] = Color("#823535", 'hex')
        colors[named("Twilight lavender")] = Color("#8A496B", 'hex')
        colors[named("Tyrian purple")] = Color("#66023C", 'hex')
        colors[named("UA blue")] = Color("#0033AA", 'hex')
        colors[named("UA red")] = Color("#D9004C", 'hex')
        colors[named("Ube")] = Color("#8878C3", 'hex')
        colors[named("UCLA Blue")] = Color("#536895", 'hex')
        colors[named("UCLA Gold")] = Color("#FFB300", 'hex')
        colors[named("UFO Green")] = Color("#3CD070", 'hex')
        colors[named("Ultramarine")] = Color("#120A8F", 'hex')
        colors[named("Ultramarine blue")] = Color("#4166F5", 'hex')
        colors[named("Ultra pink")] = Color("#FF6FFF", 'hex')
        colors[named("Umber")] = Color("#635147", 'hex')
        colors[named("United Nations blue")] = Color("#5B92E5", 'hex')
        colors[named("Unmellow Yellow")] = Color("#FFFF66", 'hex')
        colors[named("UP Forest green")] = Color("#014421", 'hex')
        colors[named("UP Maroon")] = Color("#7B1113", 'hex')
        colors[named("Upsdell red")] = Color("#AE2029", 'hex')
        colors[named("Urobilin")] = Color("#E1AD21", 'hex')
        colors[named("USC Cardinal")] = Color("#990000", 'hex')
        colors[named("USC Gold")] = Color("#FFCC00", 'hex')
        colors[named("Utah Crimson")] = Color("#D3003F", 'hex')
        colors[named("Vanilla")] = Color("#F3E5AB", 'hex')
        colors[named("Vegas gold")] = Color("#C5B358", 'hex')
        colors[named("Venetian red")] = Color("#C80815", 'hex')
        colors[named("Verdigris")] = Color("#43B3AE", 'hex')
        colors[named("Vermilion")] = Color("#E34234", 'hex')
        colors[named("Veronica")] = Color("#A020F0", 'hex')
        colors[named("Violet")] = Color("#8F00FF", 'hex')
        colors[named("Violet (color wheel)")] = Color("#7F00FF", 'hex')
        colors[named("Violet (RYB)")] = Color("#8601AF", 'hex')
        colors[named("Violet (web)")] = Color("#EE82EE", 'hex')
        colors[named("Viridian")] = Color("#40826D", 'hex')
        colors[named("Vivid auburn")] = Color("#922724", 'hex')
        colors[named("Vivid burgundy")] = Color("#9F1D35", 'hex')
        colors[named("Vivid cerise")] = Color("#DA1D81", 'hex')
        colors[named("Vivid tangerine")] = Color("#FFA089", 'hex')
        colors[named("Vivid violet")] = Color("#9F00FF", 'hex')
        colors[named("Warm black")] = Color("#004242", 'hex')
        colors[named("Wenge")] = Color("#645452", 'hex')
        colors[named("Wheat")] = Color("#F5DEB3", 'hex')
        colors[named("White")] = Color("#FFFFFF", 'hex')
        colors[named("White smoke")] = Color("#F5F5F5", 'hex')
        colors[named("Wild blue yonder")] = Color("#A2ADD0", 'hex')
        colors[named("Wild Strawberry")] = Color("#FF43A4", 'hex')
        colors[named("Wild Watermelon")] = Color("#FC6C85", 'hex')
        colors[named("Wisteria")] = Color("#C9A0DC", 'hex')
        colors[named("Xanadu")] = Color("#738678", 'hex')
        colors[named("Yale Blue")] = Color("#0F4D92", 'hex')
        colors[named("Yellow")] = Color("#FFFF00", 'hex')
        colors[named("Yellow (Munsell)")] = Color("#EFCC00", 'hex')
        colors[named("Yellow (NCS)")] = Color("#FFD300", 'hex')
        colors[named("Yellow (process)")] = Color("#FFEF00", 'hex')
        colors[named("Yellow (RYB)")] = Color("#FEFE33", 'hex')
        colors[named("Yellow-green")] = Color("#9ACD32", 'hex')
        colors[named("Zaffre")] = Color("#0014A8", 'hex')
        colors[named("Zinnwaldite brown")] = Color("#2C1608", 'hex')


Color.fill_named_colors()