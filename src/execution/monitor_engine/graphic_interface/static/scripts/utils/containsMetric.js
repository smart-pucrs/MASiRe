export default function containsMetric(metric, list) {
    for (let i = 0; i < list.length; i++) {
        if (list[i].identifier === metric.identifier && list[i].type === metric.type)
            return i;
    }

    return -1;
}