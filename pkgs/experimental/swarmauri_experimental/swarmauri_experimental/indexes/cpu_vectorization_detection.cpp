// cpu_vectorization_detection.cpp
#include <iostream>
#include <cstdint>
#include <cstdlib>

#ifdef _MSC_VER
  #include <intrin.h>
#else
  #include <cpuid.h>
#endif

// For inline assembly on non-MSVC compilers (used for xgetbv)
#if !defined(_MSC_VER)
#include <cstring>
#endif

// Check for ARM NEON support
#if defined(__ARM_NEON) || defined(__ARM_NEON__)
  #define ARM_NEON_SUPPORTED 1
#else
  #define ARM_NEON_SUPPORTED 0
#endif

// x86 CPUID wrappers:
#ifdef _MSC_VER
static void cpuid(int cpuInfo[4], int function_id, int subfunction_id = 0) {
    __cpuidex(cpuInfo, function_id, subfunction_id);
}
static uint64_t xgetbv(unsigned int index) {
    return _xgetbv(index);
}
#else
static void cpuid(int cpuInfo[4], int function_id, int subfunction_id = 0) {
    __cpuid_count(function_id, subfunction_id, cpuInfo[0], cpuInfo[1], cpuInfo[2], cpuInfo[3]);
}
static uint64_t xgetbv(unsigned int index) {
    uint32_t eax, edx;
    __asm__ __volatile__("xgetbv" : "=a"(eax), "=d"(edx) : "c"(index));
    return ((uint64_t)edx << 32) | eax;
}
#endif

// Check for SSE support (SSE is indicated by bit 25 of EDX in CPUID function 1)
bool check_x86_sse() {
#ifdef _MSC_VER
    int cpuInfo[4];
    cpuid(cpuInfo, 1);
    return (cpuInfo[3] & (1 << 25)) != 0;
#else
    unsigned int eax, ebx, ecx, edx;
    if (__get_cpuid(1, &eax, &ebx, &ecx, &edx))
        return (edx & (1 << 25)) != 0;
    return false;
#endif
}

// Check for SSE2 support (bit 26 of EDX in CPUID function 1)
bool check_x86_sse2() {
#ifdef _MSC_VER
    int cpuInfo[4];
    cpuid(cpuInfo, 1);
    return (cpuInfo[3] & (1 << 26)) != 0;
#else
    unsigned int eax, ebx, ecx, edx;
    if (__get_cpuid(1, &eax, &ebx, &ecx, &edx))
        return (edx & (1 << 26)) != 0;
    return false;
#endif
}

// Check for AVX support (bit 28 of ECX in CPUID function 1 and OS support via xgetbv)
bool check_x86_avx() {
#ifdef _MSC_VER
    int cpuInfo[4];
    cpuid(cpuInfo, 1);
    bool cpuAVX = (cpuInfo[2] & (1 << 28)) != 0;
    bool osXSAVE = (cpuInfo[2] & (1 << 27)) != 0;
    if (cpuAVX && osXSAVE) {
        uint64_t xcrFeatureMask = xgetbv(0);
        return (xcrFeatureMask & 0x6) == 0x6;
    }
    return false;
#else
    unsigned int eax, ebx, ecx, edx;
    if (!__get_cpuid(1, &eax, &ebx, &ecx, &edx)) return false;
    bool cpuAVX = (ecx & (1 << 28)) != 0;
    bool osXSAVE = (ecx & (1 << 27)) != 0;
    if (cpuAVX && osXSAVE) {
        uint32_t a, d;
        __asm__ ("xgetbv" : "=a"(a), "=d"(d) : "c"(0));
        uint64_t xcrFeatureMask = ((uint64_t)d << 32) | a;
        return (xcrFeatureMask & 0x6) == 0x6;
    }
    return false;
#endif
}

// Check for AVX2 support (bit 5 of EBX in CPUID leaf 7)
bool check_x86_avx2() {
#ifdef _MSC_VER
    int cpuInfo[4];
    cpuid(cpuInfo, 7, 0);
    return (cpuInfo[1] & (1 << 5)) != 0;
#else
    unsigned int eax, ebx, ecx, edx;
    if (__get_cpuid_count(7, 0, &eax, &ebx, &ecx, &edx))
        return (ebx & (1 << 5)) != 0;
    return false;
#endif
}

// Check for AVX512 support (bit 16 of EBX in CPUID leaf 7 and OS support)
bool check_x86_avx512() {
#ifdef _MSC_VER
    int cpuInfo[4];
    cpuid(cpuInfo, 7, 0);
    bool cpuAVX512 = (cpuInfo[1] & (1 << 16)) != 0;
    if (cpuAVX512) {
        uint64_t xcrFeatureMask = xgetbv(0);
        return (xcrFeatureMask & 0xe6) == 0xe6;
    }
    return false;
#else
    unsigned int eax, ebx, ecx, edx;
    if (__get_cpuid_count(7, 0, &eax, &ebx, &ecx, &edx)) {
        bool cpuAVX512 = (ebx & (1 << 16)) != 0;
        if (cpuAVX512) {
            uint32_t a, d;
            __asm__ ("xgetbv" : "=a"(a), "=d"(d) : "c"(0));
            uint64_t xcrFeatureMask = ((uint64_t)d << 32) | a;
            return (xcrFeatureMask & 0xe6) == 0xe6;
        }
    }
    return false;
#endif
}

// ARM: simply check if the NEON macro is defined
bool check_arm_neon() {
#if ARM_NEON_SUPPORTED
    return true;
#else
    return false;
#endif
}

int main() {
    std::cout << "CPU Vectorization Support Detection\n";
    std::cout << "-----------------------------------\n";

    // Detect the architecture:
#if defined(__x86_64__) || defined(_M_X64)
    std::cout << "Architecture: x86_64\n";
#elif defined(__i386__) || defined(_M_IX86)
    std::cout << "Architecture: x86 (32-bit)\n";
#elif defined(__aarch64__)
    std::cout << "Architecture: ARM64\n";
#elif defined(__arm__)
    std::cout << "Architecture: ARM\n";
#else
    std::cout << "Architecture: Unknown\n";
#endif

    // On x86 architectures:
#if defined(__x86_64__) || defined(__i386__) || defined(_M_X64) || defined(_M_IX86)
    std::cout << "SSE support:    " << (check_x86_sse() ? "Yes" : "No") << "\n";
    std::cout << "SSE2 support:   " << (check_x86_sse2() ? "Yes" : "No") << "\n";
    std::cout << "AVX support:    " << (check_x86_avx() ? "Yes" : "No") << "\n";
    std::cout << "AVX2 support:   " << (check_x86_avx2() ? "Yes" : "No") << "\n";
    std::cout << "AVX512 support: " << (check_x86_avx512() ? "Yes" : "No") << "\n";
#endif

    // On ARM architectures:
#if defined(__arm__) || defined(__aarch64__)
    std::cout << "NEON support:   " << (check_arm_neon() ? "Yes" : "No") << "\n";
#endif

    // Darwin (macOS) indicator:
#ifdef __APPLE__
    std::cout << "Running on Darwin (macOS)\n";
#endif

    return 0;
}
