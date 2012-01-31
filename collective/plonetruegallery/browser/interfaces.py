from zope.interface import Interface


class IPTGUtility(Interface):
    """
    utility methods for plonetruegallery
    """

    def should_include(filename):
        """
        This method can be called from an include expression for css/javascript
        to check if a file should be included for the gallery.
        """

    def enabled():
        """
        Lets you know if the gallery is enabled
        """
