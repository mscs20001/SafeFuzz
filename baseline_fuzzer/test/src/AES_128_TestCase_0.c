#include "Crypto.h"
#include "TestHarness.h"

/* Job configuration */

static Crypto_PrimitiveInfoType TestPrimitiveInfo = {
    0U, /* resultLength */
    CRYPTO_ENCRYPT, /* service */
    {
        CRYPTO_ALGOFAM_AES, /* family */
        CRYPTO_ALGOFAM_NOT_SET, /* secondaryFamily (unused for AES_128) */
        128U, /* keyLength */
        CRYPTO_ALGOMODE_ECB, /* mode */
    }, /* algorithm */
};

static Crypto_JobPrimitiveInfoType TestJobPrimitiveInfo = {
    0U, /* callbackId (unused) */
    &TestPrimitiveInfo, /* primitiveInfo */
    0U, /* secureCounterId (unused) */
    0U, /* cryIfKeyId (unused) */
    CRYPTO_PROCESSING_SYNC, /* processingType */
    FALSE, /* callbackUpdateNotification (unused) */
};

static Crypto_JobInfoType TestJobInfo = {
    0U, /* jobId */
    0U, /* jobPriority */
};

static Crypto_JobType TestJob = {
    0U, /* jobId */
    CRYPTO_JOBSTATE_IDLE, /* jobState */
    {
        NULL_PTR, /* inputPtr */
        0U, /* inputLength */
        NULL_PTR, /* secondaryInputPtr */
        0U, /* secondaryInputLength */
        NULL_PTR, /* tertiaryInputPtr */
        0U, /* tertiaryInputLength */
        NULL_PTR, /* outputPtr */
        NULL_PTR, /* outputLengthPtr */
        NULL_PTR, /* secondaryOutputPtr */
        NULL_PTR, /* secondaryOutputLengthPtr */
        0U, /* input64 */
        NULL_PTR, /* verifyPtr */
        NULL_PTR, /* output64Ptr */
        CRYPTO_OPERATIONMODE_SINGLECALL /* mode */
    }, /* jobPrimitiveInputOutput */
    &TestJobPrimitiveInfo, /* jobPrimitiveInfo */
    &TestJobInfo, /* jobInfo */
    CryptoConf_CryptoKey_TestKey_AES_00, /* cryptoKeyId */
};

void AES_128_TestCase_0(void)
{
    uint8 TestKey_0[16] = {
        0x00U, 0x01U, 0x02U, 0x03U,
        0x04U, 0x05U, 0x06U, 0x07U,
        0x08U, 0x09U, 0x0AU, 0x0BU,
        0x0CU, 0x0DU, 0x0EU, 0x0FU
    };
    uint8 TestIV_0[16] = {
        0x00U, 0x01U, 0x02U, 0x03U,
        0x04U, 0x05U, 0x06U, 0x07U,
        0x08U, 0x09U, 0x0AU, 0x0BU,
        0x0CU, 0x0DU, 0x0EU, 0x0FU
    };
    uint8 TestInput_0[1000*1000];
    uint8 TestOutput_0[16] = {0U};

    Crypto_ServiceInfoType Service;
    Crypto_AlgorithmModeType AlgoMode;
    Crypto_ProcessingType Processing;
    Crypto_OperationModeType OpMode;
    uint32 ResultLength;
    uint32 InputLength;
    uint32 OutputLength;
    uint32 ObjectId;
    uint8 DoInit;
    uint8 DoSetKeyValid;

    TestHarness_PrepareInput((void *)&ResultLength, 8);
    TestHarness_PrepareInput((void *)&Service, 8);
    TestHarness_PrepareInput((void *)&AlgoMode, 8);
    TestHarness_PrepareInput((void *)&Processing, 8);
    TestHarness_PrepareInput((void *)&InputLength, 32);
    TestHarness_PrepareInput((void *)&OutputLength, 32);
    TestHarness_PrepareInput((void *)&OpMode, 8);
    TestHarness_PrepareInput((void *)&ObjectId, 32);
    TestHarness_PrepareInput((void *)&DoInit, 1);
    TestHarness_PrepareInput((void *)&DoSetKeyValid, 1);

    /* Set up job */
    TestJob.jobPrimitiveInfo->primitiveInfo->resultLength = ResultLength;
    TestJob.jobPrimitiveInfo->primitiveInfo->service = Service;
    TestJob.jobPrimitiveInfo->primitiveInfo->algorithm.mode = AlgoMode;
    TestJob.jobPrimitiveInfo->processingType = Processing;

    /* set up input buffer */
    TestJob.jobPrimitiveInputOutput.inputPtr = &TestInput_0[0];
    TestJob.jobPrimitiveInputOutput.inputLength = InputLength;

    /* set up output buffer */
    TestJob.jobPrimitiveInputOutput.outputPtr = &TestOutput_0[0];
    TestJob.jobPrimitiveInputOutput.outputLengthPtr = &OutputLength;

    if(DoInit == 1)
    {
        /**
         * @step       Call Crypto_Init API
         * @expected   Module shall be initialized without any error
         */
        Crypto_Init();
    }

    if(DoSetKeyValid == 1)
    {
        /**
         * @step       Call Crypto_KeyElementSet API for CRYPTO_KE_CIPHER_IV
         * @expected   Module shall set AES key element without any error
         */
        (void)Crypto_KeyElementSet(CryptoConf_CryptoKey_TestKey_AES_00, CRYPTO_KE_CIPHER_IV, &TestIV_0[0], 16U);

        /**
         * @step       Call Crypto_KeyElementSet API for CRYPTO_KE_CIPHER_KEY
         * @expected   Module shall set AES key element without any error
         */
        (void)Crypto_KeyElementSet(CryptoConf_CryptoKey_TestKey_AES_00, CRYPTO_KE_CIPHER_KEY, &TestKey_0[0], 16U);

        /**
         * @step       Call Crypto_KeySetValid API
         * @expected   Module shall set AES key as VALID without any error
         */
        (void)Crypto_KeySetValid(CryptoConf_CryptoKey_TestKey_AES_00);
    }

    TestJob.jobPrimitiveInputOutput.mode = OpMode;
    (void)Crypto_ProcessJob(ObjectId, &TestJob);
}
