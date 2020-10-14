/** 
 * Defines the size of the route circle
 * @param zoom -> the zoom level of the screen
 */
export default function defineRouteRadius(zoom) {
    if (zoom > 15) {
        return 10;
    } else if (zoom >= 13) {
        return 40;
    } else if (zoom >= 11) {
        return 60;
    }

    return 80;
}