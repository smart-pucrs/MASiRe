export default function getSpeedMultiplier(speed) {
    switch (speed) {
        case 1750:
            return 0.25;
        case 1500:
            return 0.5;
        case 1250:
            return 0.75;
        case 750:
            return 1.5;
        case 500:
            return 2;
        case 250:
            return 4;
        default:
            return 1;
    }
}