#ifndef TEST_HARNESS_H
#define TEST_HARNESS_H

extern void TestHarness_PrepareInput(void * inPtr, uint8 size);
extern void TestHarness_Setup(uint32 threadId);
extern void TestHarness_Teardown(void);

#endif /* TEST_HARNESS_H */
