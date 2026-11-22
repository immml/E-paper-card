#include "management_protocol.h"
#include <string.h>

uint16_t los_crc16(const uint8_t *data, size_t length)
{
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (unsigned bit = 0; bit < 8; ++bit) crc = (crc & 1U) ? (uint16_t)((crc >> 1) ^ 0xA001U) : (uint16_t)(crc >> 1);
    }
    return crc;
}

size_t los_frame_encode(const los_frame_t *frame, uint8_t *out, size_t capacity)
{
    if (!frame || !out || frame->payload_length > LOS_PROTOCOL_MAX_PAYLOAD || capacity < LOS_PROTOCOL_HEADER_SIZE + frame->payload_length + LOS_PROTOCOL_CRC_SIZE) return 0;
    out[0] = LOS_PROTOCOL_SOF; out[1] = LOS_PROTOCOL_VERSION; out[2] = frame->command; out[3] = frame->sequence;
    out[4] = (uint8_t)frame->payload_length; out[5] = (uint8_t)(frame->payload_length >> 8); out[6] = 0;
    if (frame->payload_length) memcpy(out + LOS_PROTOCOL_HEADER_SIZE, frame->payload, frame->payload_length);
    size_t offset = LOS_PROTOCOL_HEADER_SIZE + frame->payload_length;
    uint16_t crc = los_crc16(out + 1, LOS_PROTOCOL_HEADER_SIZE - 1 + frame->payload_length);
    out[offset] = (uint8_t)crc; out[offset + 1] = (uint8_t)(crc >> 8);
    return offset + LOS_PROTOCOL_CRC_SIZE;
}

int los_frame_decode(const uint8_t *data, size_t length, los_frame_t *out, uint8_t *payload, size_t payload_capacity)
{
    if (!data || !out || length < LOS_PROTOCOL_HEADER_SIZE + LOS_PROTOCOL_CRC_SIZE || data[0] != LOS_PROTOCOL_SOF || data[1] != LOS_PROTOCOL_VERSION) return -1;
    uint16_t payload_length = (uint16_t)data[4] | ((uint16_t)data[5] << 8);
    size_t frame_length = LOS_PROTOCOL_HEADER_SIZE + payload_length + LOS_PROTOCOL_CRC_SIZE;
    if (payload_length > LOS_PROTOCOL_MAX_PAYLOAD || frame_length != length || payload_length > payload_capacity || (payload_length && !payload)) return -2;
    uint16_t expected = (uint16_t)data[length - 2] | ((uint16_t)data[length - 1] << 8);
    if (los_crc16(data + 1, LOS_PROTOCOL_HEADER_SIZE - 1 + payload_length) != expected) return -3;
    if (payload_length) memcpy(payload, data + LOS_PROTOCOL_HEADER_SIZE, payload_length);
    out->command = data[2]; out->sequence = data[3]; out->payload = payload; out->payload_length = payload_length;
    return 0;
}

bool los_sequence_is_duplicate(los_sequence_tracker_t *tracker, uint8_t sequence)
{
    if (tracker->initialized && tracker->last_sequence == sequence) return true;
    tracker->last_sequence = sequence; tracker->initialized = true; return false;
}

bool los_retry_allowed(const los_retry_policy_t *policy, uint8_t attempt)
{
    return policy && attempt < policy->attempts;
}
